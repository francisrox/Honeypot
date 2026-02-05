"""
Configuration Management for AI Scam Honeypot
Handles all system settings with environment variable support
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ScamDetectionConfig:
    """Configuration for scam detection module"""
    confidence_threshold: float = 0.85  # Minimum confidence to activate honeypot
    keyword_weight: float = 0.3  # Weight for keyword-based detection
    pattern_weight: float = 0.3  # Weight for pattern matching
    llm_weight: float = 0.4  # Weight for LLM semantic analysis
    enable_whitelist: bool = True  # Enable sender whitelist
    

@dataclass
class EngagementLimits:
    """Limits to prevent over-engagement"""
    max_messages: int = 15  # Maximum messages per conversation
    max_duration_minutes: int = 30  # Maximum conversation duration
    min_entities_for_stop: int = 3  # Stop after extracting this many high-value entities
    max_repetitions: int = 3  # Stop if scammer repeats same message
    suspicion_threshold: float = 0.7  # Stop if scammer suspicion detected


@dataclass
class LLMConfig:
    """LLM provider configuration"""
    provider: str = "openai"  # Options: openai, gemini, ollama
    model: str = "gpt-4"  # Model name
    api_key: str = ""  # API key from environment
    temperature: float = 0.7  # Response creativity (0.0-1.0)
    max_tokens: int = 150  # Maximum response length
    timeout_seconds: int = 10  # API timeout
    enable_fallback: bool = True  # Use pre-written responses if API fails
    

@dataclass
class PersonaConfig:
    """Persona management settings"""
    enable_consistency_check: bool = True  # Validate responses against history
    max_memory_items: int = 100  # Maximum conversation history to track
    typing_delay_seconds: float = 2.0  # Simulate human typing delay
    

@dataclass
class EntityExtractionConfig:
    """Entity extraction settings"""
    enable_normalization: bool = True  # Normalize extracted data
    enable_url_expansion: bool = True  # Expand shortened URLs
    min_confidence_for_report: float = 0.5  # Minimum confidence to include in report
    

@dataclass
class LegalConfig:
    """Legal and compliance settings"""
    enable_legal_disclaimers: bool = True  # Add disclaimers to reports
    enable_pii_masking: bool = True  # Mask PII in logs
    data_retention_days: int = 90  # How long to keep conversation data
    require_law_enforcement_flag: bool = False  # Require LE coordination flag
    jurisdiction: str = "IN"  # Country code for legal compliance
    

@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_to_file: bool = True  # Write logs to file
    log_file_path: str = "honeypot.log"
    enable_pii_masking: bool = True  # Mask sensitive data in logs
    

class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Load all configuration sections
        self.scam_detection = ScamDetectionConfig(
            confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.85")),
            enable_whitelist=os.getenv("ENABLE_WHITELIST", "true").lower() == "true"
        )
        
        self.engagement = EngagementLimits(
            max_messages=int(os.getenv("MAX_MESSAGES", "15")),
            max_duration_minutes=int(os.getenv("MAX_DURATION_MINUTES", "30")),
            min_entities_for_stop=int(os.getenv("MIN_ENTITIES_FOR_STOP", "3"))
        )
        
        self.llm = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            api_key=os.getenv("LLM_API_KEY", ""),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "150")),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        )
        
        self.persona = PersonaConfig(
            enable_consistency_check=os.getenv("ENABLE_CONSISTENCY_CHECK", "true").lower() == "true",
            typing_delay_seconds=float(os.getenv("TYPING_DELAY_SECONDS", "2.0"))
        )
        
        self.entity_extraction = EntityExtractionConfig(
            enable_normalization=os.getenv("ENABLE_NORMALIZATION", "true").lower() == "true",
            enable_url_expansion=os.getenv("ENABLE_URL_EXPANSION", "true").lower() == "true"
        )
        
        self.legal = LegalConfig(
            enable_legal_disclaimers=os.getenv("ENABLE_LEGAL_DISCLAIMERS", "true").lower() == "true",
            enable_pii_masking=os.getenv("ENABLE_PII_MASKING", "true").lower() == "true",
            data_retention_days=int(os.getenv("DATA_RETENTION_DAYS", "90")),
            jurisdiction=os.getenv("JURISDICTION", "IN")
        )
        
        self.logging = LoggingConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file_path=os.getenv("LOG_FILE_PATH", "honeypot.log"),
            enable_pii_masking=os.getenv("ENABLE_PII_MASKING", "true").lower() == "true"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "scam_detection": self.scam_detection.__dict__,
            "engagement": self.engagement.__dict__,
            "llm": {**self.llm.__dict__, "api_key": "***"},  # Mask API key
            "persona": self.persona.__dict__,
            "entity_extraction": self.entity_extraction.__dict__,
            "legal": self.legal.__dict__,
            "logging": self.logging.__dict__
        }
    
    def validate(self) -> tuple[bool, str]:
        """Validate configuration"""
        # Check confidence threshold
        if not 0.0 <= self.scam_detection.confidence_threshold <= 1.0:
            return False, "Confidence threshold must be between 0.0 and 1.0"
        
        # Check weights sum to 1.0
        weight_sum = (self.scam_detection.keyword_weight + 
                     self.scam_detection.pattern_weight + 
                     self.scam_detection.llm_weight)
        if abs(weight_sum - 1.0) > 0.01:
            return False, f"Detection weights must sum to 1.0 (current: {weight_sum})"
        
        # Check LLM API key
        if self.llm.provider in ["openai", "gemini"] and not self.llm.api_key:
            return False, f"API key required for {self.llm.provider}"
        
        # Check engagement limits
        if self.engagement.max_messages < 1:
            return False, "max_messages must be at least 1"
        
        return True, "Configuration valid"


# Global configuration instance
config = Config()
