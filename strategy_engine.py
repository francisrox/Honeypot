"""
Adaptive Strategy Engine with Stop Conditions
Addresses Drawbacks #3, #9: Conversation Collapse & Over-Engagement
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from config import config
from utils import logger
from entity_extractor import extractor


class StrategyPhase(Enum):
    """Conversation strategy phases"""
    BUILD_TRUST = "build_trust"  # Show interest, ask clarifying questions
    EXTRACT_INTEL = "extract_intel"  # Request payment details
    DELAY_PROBE = "delay_probe"  # Express concerns, ask for verification
    EXIT = "exit"  # Stop conversation


class StopReason(Enum):
    """Reasons for stopping conversation"""
    MAX_MESSAGES = "max_messages_reached"
    ENTITIES_EXTRACTED = "sufficient_entities_extracted"
    SCAMMER_SUSPICIOUS = "scammer_shows_suspicion"
    UNPRODUCTIVE = "conversation_unproductive"
    TIME_LIMIT = "time_limit_exceeded"
    SCAMMER_ENDED = "scammer_ended_conversation"
    DEMO_MODE = "demo_mode"
    SCAMMER_DISENGAGED = "scammer_disengaged"
    AGENT_DISENGAGED = "agent_disengaged"


@dataclass
class ConversationState:
    """Tracks conversation state"""
    message_count: int = 0
    start_time: float = 0.0
    current_phase: StrategyPhase = StrategyPhase.BUILD_TRUST
    scammer_repetitions: int = 0
    last_scammer_message: str = ""
    suspicion_indicators: List[str] = None
    
    def __post_init__(self):
        if self.suspicion_indicators is None:
            self.suspicion_indicators = []
        if self.start_time == 0.0:
            self.start_time = time.time()


class StrategyEngine:
    """Manages conversation strategy and stop conditions"""
    
    # Suspicion indicators (scammer testing if victim is real)
    SUSPICION_INDICATORS = [
        r'are you (?:a )?(?:bot|robot|ai)',
        r'are you real',
        r'send (?:me )?(?:a )?(?:voice|audio|video)',
        r'call me',
        r'video call',
        r'prove you(?:\'re| are) real',
        r'show me your (?:face|photo)',
        r'why (?:are you|you\'re) asking so many questions',
    ]
    
    # Unproductive conversation indicators
    UNPRODUCTIVE_INDICATORS = [
        r'(?:stop|leave me alone|don\'t (?:contact|message))',
        r'i\'m not interested',
        r'this is (?:a )?scam',
        r'i will (?:report|complain)',
    ]
    
    # Phase-specific strategies
    PHASE_STRATEGIES = {
        StrategyPhase.BUILD_TRUST: {
            "goal": "Establish rapport and show interest",
            "tactics": [
                "Introduce yourself with name and basic details",
                "Share your situation/need that makes this attractive",
                "Express excitement and eagerness",
                "Ask specific questions about next steps",
                "Show vulnerability and trust"
            ],
            "example_prompts": [
                "Hi! I'm [name], [age] from [location]. This sounds amazing! How do I get started?",
                "I really need this! I'm [situation]. Where should I send the payment?",
                "This is exactly what I've been looking for! What's your account number?"
            ]
        },
        StrategyPhase.EXTRACT_INTEL: {
            "goal": "Get scammer to reveal payment/contact details",
            "tactics": [
                "Volunteer payment readiness",
                "Ask for specific payment details (UPI, account, phone)",
                "Share financial situation to appear genuine",
                "Express urgency and willingness to proceed",
                "Request contact information"
            ],
            "example_prompts": [
                "I have the money ready! Should I use UPI or bank transfer? What's your ID?",
                "I can pay right now. Just tell me your account number and I'll send it.",
                "My son helped me set up online banking. What's your phone number or UPI?"
            ]
        },
        StrategyPhase.DELAY_PROBE: {
            "goal": "Extract more information while appearing cautious",
            "tactics": [
                "Share concerns while maintaining interest",
                "Mention family/friends to extract verification details",
                "Request additional contact methods",
                "Ask for proof while staying engaged",
                "Delay commitment to keep conversation going"
            ],
            "example_prompts": [
                "My daughter said to be careful. Can you send me your office address or website?",
                "I want to do this, but my friend wants to verify. What's your company registration number?",
                "I'm ready to pay, but can you also give me a WhatsApp number I can call?"
            ]
        }
    }
    
    def __init__(self):
        self.state = ConversationState()
    
    def should_stop(self) -> tuple[bool, Optional[StopReason]]:
        """Check if conversation should stop"""
        
        # Check message limit
        if self.state.message_count >= config.engagement.max_messages:
            logger.info(f"Stop condition: Max messages ({config.engagement.max_messages}) reached")
            return True, StopReason.MAX_MESSAGES
        
        # Check time limit
        elapsed_minutes = (time.time() - self.state.start_time) / 60
        if elapsed_minutes >= config.engagement.max_duration_minutes:
            logger.info(f"Stop condition: Time limit ({config.engagement.max_duration_minutes} min) exceeded")
            return True, StopReason.TIME_LIMIT
        
        # Check if sufficient entities extracted
        entity_count = extractor.get_entity_count()
        if entity_count >= config.engagement.min_entities_for_stop:
            logger.info(f"Stop condition: Sufficient entities ({entity_count}) extracted")
            return True, StopReason.ENTITIES_EXTRACTED
        
        # Check scammer suspicion
        if len(self.state.suspicion_indicators) >= 2:
            logger.info("Stop condition: Scammer showing suspicion")
            return True, StopReason.SCAMMER_SUSPICIOUS
        
        # Check repetitions (scammer repeating same message)
        if self.state.scammer_repetitions >= config.engagement.max_repetitions:
            logger.info("Stop condition: Scammer repeating messages")
            return True, StopReason.UNPRODUCTIVE
        
        return False, None
    
    def analyze_scammer_message(self, message: str) -> Dict[str, Any]:
        """Analyze scammer's message for indicators"""
        import re
        
        analysis = {
            "suspicion_detected": False,
            "unproductive_detected": False,
            "is_repetition": False,
            "indicators": []
        }
        
        # Check for suspicion indicators
        for pattern in self.SUSPICION_INDICATORS:
            if re.search(pattern, message, re.IGNORECASE):
                analysis["suspicion_detected"] = True
                analysis["indicators"].append(f"suspicion:{pattern}")
                self.state.suspicion_indicators.append(pattern)
        
        # Check for unproductive indicators
        for pattern in self.UNPRODUCTIVE_INDICATORS:
            if re.search(pattern, message, re.IGNORECASE):
                analysis["unproductive_detected"] = True
                analysis["indicators"].append(f"unproductive:{pattern}")
        
        # Check for repetition
        if message.strip().lower() == self.state.last_scammer_message.strip().lower():
            analysis["is_repetition"] = True
            self.state.scammer_repetitions += 1
        else:
            self.state.scammer_repetitions = 0
            self.state.last_scammer_message = message
        
        return analysis
    
    def determine_phase(self) -> StrategyPhase:
        """Determine current conversation phase"""
        
        # Phase progression based on message count and entities
        message_count = self.state.message_count
        entity_count = extractor.get_entity_count()
        
        # Build trust phase (first 3-5 messages)
        if message_count < 3:
            return StrategyPhase.BUILD_TRUST
        
        # Extract intel phase (after trust built, before entities extracted)
        elif message_count < 8 and entity_count < 2:
            return StrategyPhase.EXTRACT_INTEL
        
        # Delay & probe phase (after some entities, keep extracting more)
        elif entity_count >= 1 and message_count < config.engagement.max_messages - 3:
            return StrategyPhase.DELAY_PROBE
        
        # Exit phase (approaching limits)
        else:
            return StrategyPhase.EXIT
    
    def get_strategy_guidance(self) -> Dict[str, Any]:
        """Get strategy guidance for current phase"""
        
        phase = self.determine_phase()
        self.state.current_phase = phase
        
        if phase == StrategyPhase.EXIT:
            return {
                "phase": phase.value,
                "goal": "End conversation gracefully",
                "guidance": "Express thanks but indicate you need to go or think about it"
            }
        
        strategy = self.PHASE_STRATEGIES.get(phase, {})
        
        return {
            "phase": phase.value,
            "goal": strategy.get("goal", ""),
            "tactics": strategy.get("tactics", []),
            "example_prompts": strategy.get("example_prompts", [])
        }
    
    def increment_message_count(self):
        """Increment message counter"""
        self.state.message_count += 1
    
    def get_adaptive_prompt_addition(self, scammer_message: str) -> str:
        """Get adaptive prompt addition based on scammer's message"""
        
        # Analyze scammer's message
        analysis = self.analyze_scammer_message(scammer_message)
        
        # Handle suspicion
        if analysis["suspicion_detected"]:
            return """
IMPORTANT: The scammer is testing if you're real. 
- DO NOT reveal you're AI
- Make excuses for not sending voice/video (broken camera, shy, etc.)
- Act more human-like with natural responses
"""
        
        # Handle requests for voice/image
        import re
        if re.search(r'(?:voice|audio|video|call|photo|picture)', scammer_message, re.IGNORECASE):
            return """
IMPORTANT: Scammer wants voice/video.
Respond with a text-based excuse:
- "My camera is broken"
- "I can't do voice calls right now, I'm at work"
- "I prefer to chat by text"
- "My phone doesn't have good audio"
"""
        
        # Handle unexpected questions
        if '?' in scammer_message and len(scammer_message.split()) < 10:
            return """
IMPORTANT: Scammer asked a direct question.
- Answer briefly and deflect back to the scam topic
- Stay in character
- Don't overthink it
"""
        
        return ""
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current state summary"""
        elapsed_minutes = (time.time() - self.state.start_time) / 60
        
        return {
            "message_count": self.state.message_count,
            "elapsed_minutes": round(elapsed_minutes, 2),
            "current_phase": self.state.current_phase.value,
            "entities_extracted": extractor.get_entity_count(),
            "suspicion_indicators": len(self.state.suspicion_indicators),
            "scammer_repetitions": self.state.scammer_repetitions
        }


# Global strategy engine instance
strategy = StrategyEngine()
