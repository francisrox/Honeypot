"""
Entity Extraction with Normalization and Verification
Addresses Drawbacks #5, #12: Poor Extraction & Fake Intelligence
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from utils import logger, DataNormalizer
from config import config


class EntityType(Enum):
    """Types of entities to extract"""
    BANK_ACCOUNT = "bank_account"
    UPI_ID = "upi_id"
    PHONE_NUMBER = "phone_number"
    URL = "url"
    EMAIL = "email"
    CRYPTO_ADDRESS = "crypto_address"
    NAME = "name"


class ConfidenceLevel(Enum):
    """Confidence levels for extracted entities"""
    HIGH = "high"  # Explicitly provided by scammer
    MEDIUM = "medium"  # Extracted from context
    LOW = "low"  # Possibly fake or test data
    NEEDS_VERIFICATION = "needs_verification"  # Suspicious patterns


@dataclass
class ExtractedEntity:
    """Extracted entity with metadata"""
    entity_type: EntityType
    value: str
    normalized_value: str
    confidence: ConfidenceLevel
    context: str  # Surrounding text
    source_message: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.entity_type.value,
            "value": self.value,
            "normalized_value": self.normalized_value,
            "confidence": self.confidence.value,
            "context": self.context
        }


class EntityExtractor:
    """Extracts and normalizes fraud infrastructure data"""
    
    # Enhanced regex patterns
    PATTERNS = {
        EntityType.BANK_ACCOUNT: [
            r'\b(\d[\s\-]*){9,18}\b',  # 9-18 digits with optional spaces/dashes
            r'account\s*(?:number|no\.?|#)?\s*:?\s*(\d[\s\-]*){9,18}',
        ],
        EntityType.UPI_ID: [
            r'\b([a-zA-Z0-9._-]+)@([a-zA-Z0-9.-]+)\b',
            r'\b([a-zA-Z0-9._-]+)\s*(?:\(at\)|\[at\]|at)\s*([a-zA-Z0-9.-]+)\b',
        ],
        EntityType.PHONE_NUMBER: [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\b(\d[\s\-]*){10,15}\b',
        ],
        EntityType.URL: [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'bit\.ly/[^\s]+',
            r'tinyurl\.com/[^\s]+',
        ],
        EntityType.EMAIL: [
            r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        ],
        EntityType.CRYPTO_ADDRESS: [
            r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',  # Bitcoin
            r'\b0x[a-fA-F0-9]{40}\b',  # Ethereum
        ],
    }
    
    def __init__(self):
        self.extracted_entities: List[ExtractedEntity] = []
    
    def extract(self, message: str, role: str = "scammer") -> List[ExtractedEntity]:
        """Extract all entities from a message"""
        entities = []
        
        # Extract each entity type
        for entity_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                
                for match in matches:
                    raw_value = match.group(0)
                    
                    # Skip if it's part of a legitimate domain (for UPI/email)
                    if entity_type == EntityType.UPI_ID:
                        if self._is_likely_email(raw_value):
                            continue
                    
                    # Normalize the value
                    normalized_value = self._normalize(raw_value, entity_type)
                    
                    # Determine confidence level
                    confidence = self._assess_confidence(normalized_value, entity_type, message, role)
                    
                    # Get context (surrounding text)
                    context = self._get_context(message, match.start(), match.end())
                    
                    entity = ExtractedEntity(
                        entity_type=entity_type,
                        value=raw_value,
                        normalized_value=normalized_value,
                        confidence=confidence,
                        context=context,
                        source_message=message
                    )
                    
                    entities.append(entity)
                    logger.debug(f"Extracted {entity_type.value}: {normalized_value} (confidence: {confidence.value})")
        
        # Add to global list (deduplicate)
        for entity in entities:
            if not self._is_duplicate(entity):
                self.extracted_entities.append(entity)
        
        return entities
    
    def _normalize(self, value: str, entity_type: EntityType) -> str:
        """Normalize extracted value"""
        if not config.entity_extraction.enable_normalization:
            return value
        
        if entity_type == EntityType.BANK_ACCOUNT:
            return DataNormalizer.normalize_bank_account(value)
        
        elif entity_type == EntityType.UPI_ID:
            return DataNormalizer.normalize_upi(value)
        
        elif entity_type == EntityType.PHONE_NUMBER:
            return DataNormalizer.normalize_phone(value)
        
        elif entity_type == EntityType.URL:
            normalized = DataNormalizer.normalize_url(value)
            # Optionally expand shortened URLs
            if config.entity_extraction.enable_url_expansion:
                normalized = self._expand_url(normalized)
            return normalized
        
        else:
            return value.strip()
    
    def _expand_url(self, url: str) -> str:
        """Expand shortened URLs"""
        try:
            import requests
            response = requests.head(url, allow_redirects=True, timeout=3)
            return response.url
        except:
            logger.warning(f"Failed to expand URL: {url}")
            return url
    
    def _assess_confidence(self, value: str, entity_type: EntityType, 
                          message: str, role: str) -> ConfidenceLevel:
        """Assess confidence level of extracted entity"""
        
        # If victim said it, it's not intelligence (victim doesn't have scammer's details)
        if role == "victim":
            return ConfidenceLevel.LOW
        
        # Check if it's likely fake
        if DataNormalizer.is_likely_fake(value, entity_type.value):
            return ConfidenceLevel.NEEDS_VERIFICATION
        
        # Check if explicitly provided (high confidence indicators)
        high_confidence_patterns = [
            r'(?:my|our)\s+(?:account|upi|number|phone)',
            r'(?:send|transfer|pay)\s+(?:to|at)',
            r'(?:use|enter)\s+(?:this|the)',
        ]
        
        for pattern in high_confidence_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return ConfidenceLevel.HIGH
        
        # Medium confidence by default (extracted from context)
        return ConfidenceLevel.MEDIUM
    
    def _get_context(self, message: str, start: int, end: int, window: int = 30) -> str:
        """Get surrounding context for entity"""
        context_start = max(0, start - window)
        context_end = min(len(message), end + window)
        return message[context_start:context_end]
    
    def _is_likely_email(self, value: str) -> bool:
        """Check if UPI ID is actually an email"""
        email_domains = ['.com', '.org', '.net', '.in', '.co', '.edu', '.gov']
        return any(value.lower().endswith(domain) for domain in email_domains)
    
    def _is_duplicate(self, entity: ExtractedEntity) -> bool:
        """Check if entity already extracted"""
        for existing in self.extracted_entities:
            if (existing.entity_type == entity.entity_type and 
                existing.normalized_value == entity.normalized_value):
                return True
        return False
    
    def get_high_value_entities(self) -> List[ExtractedEntity]:
        """Get entities with high confidence"""
        return [
            e for e in self.extracted_entities 
            if e.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]
        ]
    
    def get_entity_count(self) -> int:
        """Get count of high-value entities"""
        return len(self.get_high_value_entities())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all entities to dictionary"""
        return {
            "total_entities": len(self.extracted_entities),
            "high_value_entities": len(self.get_high_value_entities()),
            "entities_by_type": self._group_by_type(),
            "all_entities": [e.to_dict() for e in self.extracted_entities]
        }
    
    def _group_by_type(self) -> Dict[str, int]:
        """Group entities by type"""
        counts = {}
        for entity in self.extracted_entities:
            entity_type = entity.entity_type.value
            counts[entity_type] = counts.get(entity_type, 0) + 1
        return counts


# Global extractor instance
extractor = EntityExtractor()
