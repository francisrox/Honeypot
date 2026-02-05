"""
Shared Utilities for AI Scam Honeypot
Provides logging, data normalization, and helper functions
"""

import re
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from config import config


class PIIMasker:
    """Masks personally identifiable information in logs"""
    
    @staticmethod
    def mask_phone(text: str) -> str:
        """Mask phone numbers: +91-9876543210 -> +91-98765*****"""
        pattern = r'(\+?\d{1,3}[-.\s]?)(\d{3,5})([-.\s]?\d{4,10})'
        return re.sub(pattern, r'\1\2*****', text)
    
    @staticmethod
    def mask_email(text: str) -> str:
        """Mask emails: test@example.com -> t***@example.com"""
        pattern = r'([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        return re.sub(pattern, r'\1***@\2', text)
    
    @staticmethod
    def mask_bank_account(text: str) -> str:
        """Mask bank accounts: 1234567890 -> 1234***890"""
        pattern = r'\b(\d{4})\d+(\d{3})\b'
        return re.sub(pattern, r'\1***\2', text)
    
    @staticmethod
    def mask_upi(text: str) -> str:
        """Mask UPI IDs: user@upi -> u***@upi"""
        pattern = r'([a-zA-Z0-9])[a-zA-Z0-9._-]*@([a-zA-Z0-9.-]+)'
        return re.sub(pattern, r'\1***@\2', text)
    
    @staticmethod
    def mask_all(text: str) -> str:
        """Apply all masking rules"""
        text = PIIMasker.mask_phone(text)
        text = PIIMasker.mask_email(text)
        text = PIIMasker.mask_bank_account(text)
        text = PIIMasker.mask_upi(text)
        return text


class HoneypotLogger:
    """Custom logger with PII masking"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.logging.log_level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        if config.logging.log_to_file:
            file_handler = logging.FileHandler(config.logging.log_file_path)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def _mask_if_enabled(self, message: str) -> str:
        """Mask PII if enabled in config"""
        if config.logging.enable_pii_masking:
            return PIIMasker.mask_all(message)
        return message
    
    def debug(self, message: str):
        self.logger.debug(self._mask_if_enabled(message))
    
    def info(self, message: str):
        self.logger.info(self._mask_if_enabled(message))
    
    def warning(self, message: str):
        self.logger.warning(self._mask_if_enabled(message))
    
    def error(self, message: str):
        self.logger.error(self._mask_if_enabled(message))
    
    def critical(self, message: str):
        self.logger.critical(self._mask_if_enabled(message))


class DataNormalizer:
    """Normalizes extracted data for consistency"""
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Remove spaces, dashes, parentheses from phone numbers"""
        # Remove all non-digit characters except leading +
        normalized = re.sub(r'[^\d+]', '', phone)
        return normalized
    
    @staticmethod
    def normalize_bank_account(account: str) -> str:
        """Remove spaces and dashes from bank account numbers"""
        return re.sub(r'[\s\-]', '', account)
    
    @staticmethod
    def normalize_upi(upi: str) -> str:
        """Handle obfuscated UPI IDs: fraud(at)upi -> fraud@upi"""
        upi = upi.replace('(at)', '@')
        upi = upi.replace('[at]', '@')
        upi = upi.replace(' at ', '@')
        return upi.lower().strip()
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Ensure URL has protocol"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    @staticmethod
    def is_likely_fake(value: str, entity_type: str) -> bool:
        """Detect obviously fake data"""
        # Check for sequential or repeated digits
        if entity_type in ['bank_account', 'phone']:
            # Remove non-digits
            digits = re.sub(r'\D', '', value)
            
            # Check for sequential: 1234567890
            if len(digits) >= 6:
                is_sequential = all(
                    int(digits[i]) == int(digits[i-1]) + 1 
                    for i in range(1, min(6, len(digits)))
                )
                if is_sequential:
                    return True
            
            # Check for repeated: 1111111111
            if len(set(digits)) <= 2:
                return True
        
        # Check for test/dummy keywords
        test_keywords = ['test', 'dummy', 'fake', 'example', '000000', '999999']
        value_lower = value.lower()
        if any(keyword in value_lower for keyword in test_keywords):
            return True
        
        return False


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + 'Z'


def safe_json_dumps(data: Any, indent: int = 2) -> str:
    """Safely serialize data to JSON"""
    try:
        return json.dumps(data, indent=indent, default=str)
    except Exception as e:
        return json.dumps({"error": f"Serialization failed: {str(e)}"})


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL"""
    pattern = r'(?:https?://)?(?:www\.)?([^/]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def calculate_weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted average score"""
    if not scores or not weights:
        return 0.0
    
    total_score = sum(scores.get(key, 0.0) * weight for key, weight in weights.items())
    total_weight = sum(weights.values())
    
    return total_score / total_weight if total_weight > 0 else 0.0


# Create default logger
logger = HoneypotLogger("honeypot")
