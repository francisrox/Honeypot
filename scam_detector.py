"""
Multi-Layer Scam Detection with Confidence Scoring
Addresses Drawback #1: False Positives
"""

import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from config import config
from utils import logger, calculate_weighted_score
from llm_interface import llm


class ScamType(Enum):
    """Types of scams the system can detect"""
    JOB_SCAM = "job_scam"
    INVESTMENT_SCAM = "investment_scam"
    BANKING_FRAUD = "banking_fraud"
    ROMANCE_SCAM = "romance_scam"
    PRIZE_LOTTERY = "prize_lottery"
    TECH_SUPPORT = "tech_support"
    IMPERSONATION = "impersonation"
    UNKNOWN = "unknown"
    NOT_SCAM = "not_scam"


@dataclass
class ScamDetectionResult:
    """Result of scam detection analysis"""
    is_scam: bool
    confidence: float  # 0.0 to 1.0
    scam_type: ScamType
    reasoning: str
    layer_scores: Dict[str, float]  # Scores from each detection layer
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_scam": self.is_scam,
            "confidence": self.confidence,
            "scam_type": self.scam_type.value,
            "reasoning": self.reasoning,
            "layer_scores": self.layer_scores
        }


class KeywordDetector:
    """Layer 1: Keyword-based detection"""
    
    # Scam indicator keywords by category
    URGENCY_KEYWORDS = [
        "urgent", "immediately", "act now", "limited time", "expires today",
        "last chance", "hurry", "quick", "asap", "right now"
    ]
    
    MONEY_KEYWORDS = [
        "money", "cash", "payment", "transfer", "deposit", "account",
        "bank", "upi", "paytm", "gpay", "phonepe", "wallet", "₹", "$",
        "lakh", "crore", "thousand", "investment", "profit", "earn"
    ]
    
    THREAT_KEYWORDS = [
        "blocked", "suspended", "deactivated", "frozen", "locked",
        "arrest", "legal action", "police", "court", "fine", "penalty",
        "unauthorized", "suspicious activity", "security alert"
    ]
    
    REQUEST_KEYWORDS = [
        "send", "provide", "share", "verify", "confirm", "update",
        "click", "download", "install", "enter", "submit", "reply"
    ]
    
    PRIZE_KEYWORDS = [
        "won", "winner", "prize", "lottery", "lucky", "selected",
        "congratulations", "reward", "gift", "free", "bonus"
    ]
    
    JOB_KEYWORDS = [
        "job", "work from home", "part time", "earn money", "hiring",
        "opportunity", "registration fee", "training fee", "joining fee"
    ]
    
    # Legitimate sender patterns (whitelist)
    LEGITIMATE_PATTERNS = [
        r'@amazon\.com$',
        r'@google\.com$',
        r'@microsoft\.com$',
        r'@linkedin\.com$',
        r'-[A-Z]{6}$',  # Standard bank message IDs
    ]
    
    @staticmethod
    def detect(message: str, sender: Optional[str] = None) -> Dict[str, Any]:
        """Detect scam indicators using keywords"""
        message_lower = message.lower()
        
        # Check whitelist first
        if sender and config.scam_detection.enable_whitelist:
            for pattern in KeywordDetector.LEGITIMATE_PATTERNS:
                if re.search(pattern, sender, re.IGNORECASE):
                    logger.debug(f"Sender {sender} matches whitelist pattern")
                    return {
                        "score": 0.0,
                        "scam_type": ScamType.NOT_SCAM,
                        "indicators": ["whitelisted_sender"]
                    }
        
        # Count keyword matches
        indicators = []
        urgency_count = sum(1 for kw in KeywordDetector.URGENCY_KEYWORDS if kw in message_lower)
        money_count = sum(1 for kw in KeywordDetector.MONEY_KEYWORDS if kw in message_lower)
        threat_count = sum(1 for kw in KeywordDetector.THREAT_KEYWORDS if kw in message_lower)
        request_count = sum(1 for kw in KeywordDetector.REQUEST_KEYWORDS if kw in message_lower)
        prize_count = sum(1 for kw in KeywordDetector.PRIZE_KEYWORDS if kw in message_lower)
        job_count = sum(1 for kw in KeywordDetector.JOB_KEYWORDS if kw in message_lower)
        
        # Determine scam type based on keyword patterns
        scam_type = ScamType.UNKNOWN
        if prize_count >= 2:
            scam_type = ScamType.PRIZE_LOTTERY
            indicators.append("prize_keywords")
        elif job_count >= 2 and money_count >= 1:
            scam_type = ScamType.JOB_SCAM
            indicators.append("job_keywords")
        elif threat_count >= 2:
            scam_type = ScamType.BANKING_FRAUD
            indicators.append("threat_keywords")
        elif money_count >= 3:
            scam_type = ScamType.INVESTMENT_SCAM
            indicators.append("money_keywords")
        
        # Calculate score based on keyword density
        total_keywords = urgency_count + money_count + threat_count + request_count + prize_count + job_count
        
        # High urgency + money/threat is strong indicator
        if urgency_count >= 2 and (money_count >= 2 or threat_count >= 2):
            indicators.append("urgency_with_money_or_threat")
            score = 0.8
        elif total_keywords >= 5:
            indicators.append("high_keyword_density")
            score = 0.7
        elif total_keywords >= 3:
            indicators.append("moderate_keyword_density")
            score = 0.5
        elif total_keywords >= 1:
            score = 0.3
        else:
            score = 0.0
        
        return {
            "score": min(score, 1.0),
            "scam_type": scam_type,
            "indicators": indicators
        }


class PatternDetector:
    """Layer 2: Pattern matching for suspicious elements"""
    
    # Regex patterns for suspicious elements
    PHONE_PATTERN = r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    BANK_ACCOUNT_PATTERN = r'\b\d{9,18}\b'
    UPI_PATTERN = r'[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+'
    URL_PATTERN = r'https?://[^\s]+|www\.[^\s]+|bit\.ly/[^\s]+|tinyurl\.com/[^\s]+'
    
    # Suspicious URL patterns
    SUSPICIOUS_DOMAINS = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 't.co',  # URL shorteners
        '.tk', '.ml', '.ga', '.cf',  # Free domains
    ]
    
    @staticmethod
    def detect(message: str) -> Dict[str, Any]:
        """Detect suspicious patterns"""
        indicators = []
        score = 0.0
        
        # Check for phone numbers
        phone_matches = re.findall(PatternDetector.PHONE_PATTERN, message)
        if phone_matches:
            indicators.append(f"phone_numbers:{len(phone_matches)}")
            score += 0.2
        
        # Check for bank accounts
        bank_matches = re.findall(PatternDetector.BANK_ACCOUNT_PATTERN, message)
        if bank_matches:
            indicators.append(f"bank_accounts:{len(bank_matches)}")
            score += 0.3
        
        # Check for UPI IDs
        upi_matches = re.findall(PatternDetector.UPI_PATTERN, message)
        # Filter out email addresses (common false positive)
        upi_matches = [u for u in upi_matches if not u.endswith(('.com', '.org', '.net', '.in'))]
        if upi_matches:
            indicators.append(f"upi_ids:{len(upi_matches)}")
            score += 0.3
        
        # Check for URLs
        url_matches = re.findall(PatternDetector.URL_PATTERN, message)
        if url_matches:
            indicators.append(f"urls:{len(url_matches)}")
            score += 0.1
            
            # Check for suspicious domains
            for url in url_matches:
                if any(domain in url.lower() for domain in PatternDetector.SUSPICIOUS_DOMAINS):
                    indicators.append("suspicious_url")
                    score += 0.3
                    break
        
        # Multiple payment methods mentioned is suspicious
        payment_methods = ['upi', 'paytm', 'gpay', 'phonepe', 'bank account', 'account number']
        payment_count = sum(1 for pm in payment_methods if pm in message.lower())
        if payment_count >= 2:
            indicators.append("multiple_payment_methods")
            score += 0.2
        
        # Check for obfuscated text (spaces in numbers)
        if re.search(r'\d\s+\d\s+\d', message):
            indicators.append("obfuscated_numbers")
            score += 0.2
        
        return {
            "score": min(score, 1.0),
            "indicators": indicators
        }


class ScamDetector:
    """Main scam detection class with multi-layer analysis"""
    
    def __init__(self):
        self.keyword_detector = KeywordDetector()
        self.pattern_detector = PatternDetector()
    
    def detect(self, message: str, sender: Optional[str] = None) -> ScamDetectionResult:
        """
        Perform multi-layer scam detection
        
        Args:
            message: The message to analyze
            sender: Optional sender identifier for whitelist checking
        
        Returns:
            ScamDetectionResult with confidence score and reasoning
        """
        logger.info(f"Analyzing message for scam indicators (sender: {sender})")
        
        # Layer 1: Keyword detection
        keyword_result = self.keyword_detector.detect(message, sender)
        keyword_score = keyword_result["score"]
        
        # Layer 2: Pattern detection
        pattern_result = self.pattern_detector.detect(message)
        pattern_score = pattern_result["score"]
        
        # Layer 3: LLM semantic analysis
        llm_result = llm.detect_scam(message)
        llm_score = llm_result.get("confidence", 0.0) if llm_result.get("is_scam", False) else 0.0
        
        # Calculate weighted confidence score
        weights = {
            "keyword": config.scam_detection.keyword_weight,
            "pattern": config.scam_detection.pattern_weight,
            "llm": config.scam_detection.llm_weight
        }
        
        scores = {
            "keyword": keyword_score,
            "pattern": pattern_score,
            "llm": llm_score
        }
        
        final_confidence = calculate_weighted_score(scores, weights)
        
        # Determine if it's a scam based on threshold
        is_scam = final_confidence >= config.scam_detection.confidence_threshold
        
        # Determine scam type
        if keyword_result["scam_type"] != ScamType.UNKNOWN:
            scam_type = keyword_result["scam_type"]
        elif llm_result.get("scam_type"):
            try:
                scam_type = ScamType(llm_result["scam_type"])
            except:
                scam_type = ScamType.UNKNOWN
        else:
            scam_type = ScamType.UNKNOWN if is_scam else ScamType.NOT_SCAM
        
        # Build reasoning
        reasoning_parts = []
        if keyword_result["indicators"]:
            reasoning_parts.append(f"Keywords: {', '.join(keyword_result['indicators'])}")
        if pattern_result["indicators"]:
            reasoning_parts.append(f"Patterns: {', '.join(pattern_result['indicators'])}")
        if llm_result.get("reasoning"):
            reasoning_parts.append(f"LLM: {llm_result['reasoning']}")
        
        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "No strong indicators"
        
        result = ScamDetectionResult(
            is_scam=is_scam,
            confidence=final_confidence,
            scam_type=scam_type,
            reasoning=reasoning,
            layer_scores=scores
        )
        
        logger.info(f"Detection result: is_scam={is_scam}, confidence={final_confidence:.2f}, type={scam_type.value}")
        
        return result


# Global detector instance
detector = ScamDetector()
