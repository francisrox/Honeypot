"""
Persona Management with Locked Attributes and Conversation Memory
Addresses Drawbacks #2, #4: AI Behavior & Persona Consistency
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from config import config
from utils import logger
from scam_detector import ScamType


class PersonaType(Enum):
    """Types of vulnerable personas"""
    ELDERLY = "elderly"
    JOB_SEEKER = "job_seeker"
    INVESTOR = "investor"
    TECH_NOVICE = "tech_novice"
    STUDENT = "student"


@dataclass
class PersonaProfile:
    """Immutable persona attributes"""
    persona_type: PersonaType
    name: str
    age: int
    location: str
    occupation: str
    tech_knowledge: str  # low, medium, high
    financial_status: str
    family_status: str
    personality_traits: List[str]
    vulnerabilities: List[str]
    
    # Behavioral constraints
    max_typing_speed_wpm: int = 40  # Words per minute
    makes_typos: bool = True
    uses_emojis: bool = False
    
    def to_context_string(self) -> str:
        """Convert persona to context string for LLM"""
        return f"""You are {self.name}, a {self.age}-year-old {self.occupation} from {self.location}.

BACKGROUND:
- Financial status: {self.financial_status}
- Family: {self.family_status}
- Tech knowledge: {self.tech_knowledge}
- Personality: {', '.join(self.personality_traits)}

IMPORTANT CONSTRAINTS:
- You have {self.tech_knowledge} technical knowledge
- You type at about {self.max_typing_speed_wpm} words per minute
- {'You sometimes make typos' if self.makes_typos else 'You type carefully'}
- {'You use emojis' if self.uses_emojis else 'You rarely use emojis'}

VULNERABILITIES (why you might fall for scams):
{chr(10).join(f'- {v}' for v in self.vulnerabilities)}

CRITICAL: In your FIRST response, naturally introduce yourself by mentioning:
- Your name: "{self.name}"
- Your age or situation: "{self.age} years old" or "{self.occupation}"
- Why you're interested (relate to your vulnerabilities)
- Ask specific questions about payment/contact details

REMEMBER: You must stay consistent with these facts throughout the conversation."""


@dataclass
class ConversationMemory:
    """Tracks conversation history and persona statements"""
    messages: List[Dict[str, str]] = field(default_factory=list)
    persona_statements: List[str] = field(default_factory=list)  # Facts stated by persona
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp()
        })
        
        # Extract persona statements (things persona said about themselves)
        if role == "victim":
            self._extract_persona_statements(content)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def _extract_persona_statements(self, message: str):
        """Extract factual statements persona made about themselves"""
        # Look for patterns like "I am...", "My...", "I have...", etc.
        patterns = [
            r"I am (\d+) years? old",
            r"I(?:'m| am) (?:a |an )?([a-zA-Z\s]+)",
            r"My ([a-zA-Z\s]+) is ([a-zA-Z\s]+)",
            r"I (?:live|work) in ([a-zA-Z\s]+)",
            r"I have ([a-zA-Z\s]+)",
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                for match in matches:
                    statement = f"Stated: {match if isinstance(match, str) else ' '.join(match)}"
                    if statement not in self.persona_statements:
                        self.persona_statements.append(statement)
    
    def get_recent_messages(self, count: int = 5) -> List[Dict[str, str]]:
        """Get recent messages for context"""
        return self.messages[-count:]
    
    def check_consistency(self, new_statement: str, persona: PersonaProfile) -> tuple[bool, Optional[str]]:
        """Check if new statement is consistent with persona and history"""
        
        # Check age consistency
        import re
        age_match = re.search(r"I am (\d+) years? old", new_statement, re.IGNORECASE)
        if age_match:
            stated_age = int(age_match.group(1))
            if stated_age != persona.age:
                return False, f"Age inconsistency: persona is {persona.age} but stated {stated_age}"
        
        # Check occupation consistency
        occupation_patterns = [
            r"I(?:'m| am) (?:a |an )?([a-zA-Z\s]+)",
            r"I work as (?:a |an )?([a-zA-Z\s]+)"
        ]
        for pattern in occupation_patterns:
            match = re.search(pattern, new_statement, re.IGNORECASE)
            if match:
                stated_occupation = match.group(1).strip().lower()
                # Allow some variation (e.g., "retired teacher" vs "teacher")
                if persona.occupation.lower() not in stated_occupation and stated_occupation not in persona.occupation.lower():
                    # Check if it's a reasonable variation
                    if not self._is_reasonable_occupation_variation(persona.occupation, stated_occupation):
                        return False, f"Occupation inconsistency: persona is {persona.occupation} but stated {stated_occupation}"
        
        # Check location consistency
        location_match = re.search(r"I (?:live|am) in ([a-zA-Z\s]+)", new_statement, re.IGNORECASE)
        if location_match:
            stated_location = location_match.group(1).strip().lower()
            if persona.location.lower() not in stated_location and stated_location not in persona.location.lower():
                return False, f"Location inconsistency: persona is in {persona.location} but stated {stated_location}"
        
        # Check against previous statements
        for prev_statement in self.persona_statements:
            # This is a simplified check - in production, use more sophisticated NLP
            pass
        
        return True, None
    
    def _is_reasonable_occupation_variation(self, original: str, stated: str) -> bool:
        """Check if occupation variation is reasonable"""
        # Allow variations like "retired X" or "former X"
        variations = [
            f"retired {original.lower()}",
            f"former {original.lower()}",
            original.lower()
        ]
        return any(var in stated.lower() or stated.lower() in var for var in variations)


class PersonaManager:
    """Manages persona selection and consistency"""
    
    # Pre-defined persona profiles
    PERSONAS = {
        PersonaType.ELDERLY: PersonaProfile(
            persona_type=PersonaType.ELDERLY,
            name="Rajesh Kumar",
            age=68,
            location="Pune, India",
            occupation="Retired bank employee",
            tech_knowledge="low",
            financial_status="Has retirement savings, looking to invest",
            family_status="Widower, two children living abroad",
            personality_traits=["trusting", "polite", "cautious with money", "lonely"],
            vulnerabilities=[
                "Limited understanding of digital payments",
                "Trusts people who sound professional",
                "Wants to help children financially",
                "Feels isolated and appreciates attention"
            ],
            max_typing_speed_wpm=25,
            makes_typos=True,
            uses_emojis=False
        ),
        
        PersonaType.JOB_SEEKER: PersonaProfile(
            persona_type=PersonaType.JOB_SEEKER,
            name="Priya Sharma",
            age=24,
            location="Delhi, India",
            occupation="Recent graduate, looking for work",
            tech_knowledge="medium",
            financial_status="Student loans, needs income urgently",
            family_status="Single, lives with parents",
            personality_traits=["eager", "optimistic", "inexperienced", "ambitious"],
            vulnerabilities=[
                "Desperate for job opportunities",
                "Willing to pay small fees for 'guaranteed' jobs",
                "Lacks experience spotting job scams",
                "Trusts official-looking communications"
            ],
            max_typing_speed_wpm=45,
            makes_typos=False,
            uses_emojis=True
        ),
        
        PersonaType.INVESTOR: PersonaProfile(
            persona_type=PersonaType.INVESTOR,
            name="Amit Patel",
            age=42,
            location="Mumbai, India",
            occupation="Small business owner",
            tech_knowledge="medium",
            financial_status="Has savings, wants higher returns",
            family_status="Married with two children",
            personality_traits=["ambitious", "risk-taker", "busy", "greedy"],
            vulnerabilities=[
                "Attracted to high-return promises",
                "FOMO (fear of missing out) on opportunities",
                "Too busy to verify thoroughly",
                "Overconfident in financial knowledge"
            ],
            max_typing_speed_wpm=50,
            makes_typos=False,
            uses_emojis=False
        ),
        
        PersonaType.TECH_NOVICE: PersonaProfile(
            persona_type=PersonaType.TECH_NOVICE,
            name="Sunita Reddy",
            age=35,
            location="Bangalore, India",
            occupation="Homemaker",
            tech_knowledge="low",
            financial_status="Manages household finances",
            family_status="Married, husband works in IT",
            personality_traits=["careful", "confused by tech", "helpful", "worried"],
            vulnerabilities=[
                "Easily confused by technical terms",
                "Fears account being blocked/frozen",
                "Follows instructions when panicked",
                "Trusts authority figures"
            ],
            max_typing_speed_wpm=30,
            makes_typos=True,
            uses_emojis=False
        ),
        
        PersonaType.STUDENT: PersonaProfile(
            persona_type=PersonaType.STUDENT,
            name="Arjun Singh",
            age=20,
            location="Kolkata, India",
            occupation="College student",
            tech_knowledge="high",
            financial_status="Limited pocket money, wants extra income",
            family_status="Single, lives in hostel",
            personality_traits=["tech-savvy", "naive about scams", "greedy", "impulsive"],
            vulnerabilities=[
                "Wants easy money for expenses",
                "Overconfident in tech abilities",
                "Doesn't consult parents before decisions",
                "Attracted to 'work from home' offers"
            ],
            max_typing_speed_wpm=60,
            makes_typos=False,
            uses_emojis=True
        ),
    }
    
    def __init__(self):
        self.current_persona: Optional[PersonaProfile] = None
        self.memory: Optional[ConversationMemory] = None
    
    def select_persona(self, scam_type: ScamType) -> PersonaProfile:
        """Select appropriate persona based on scam type"""
        
        # Map scam types to persona types
        persona_mapping = {
            ScamType.JOB_SCAM: PersonaType.JOB_SEEKER,
            ScamType.INVESTMENT_SCAM: PersonaType.INVESTOR,
            ScamType.BANKING_FRAUD: PersonaType.TECH_NOVICE,
            ScamType.PRIZE_LOTTERY: PersonaType.ELDERLY,
            ScamType.TECH_SUPPORT: PersonaType.TECH_NOVICE,
            ScamType.ROMANCE_SCAM: PersonaType.ELDERLY,
            ScamType.IMPERSONATION: PersonaType.TECH_NOVICE,
        }
        
        persona_type = persona_mapping.get(scam_type, PersonaType.TECH_NOVICE)
        self.current_persona = self.PERSONAS[persona_type]
        self.memory = ConversationMemory()
        
        logger.info(f"Selected persona: {self.current_persona.name} ({persona_type.value}) for scam type {scam_type.value}")
        
        return self.current_persona
    
    def add_message(self, role: str, content: str):
        """Add message to conversation memory"""
        if self.memory:
            self.memory.add_message(role, content)
    
    def validate_response(self, response: str) -> tuple[bool, Optional[str]]:
        """Validate response for consistency"""
        if not self.current_persona or not self.memory:
            return True, None
        
        if not config.persona.enable_consistency_check:
            return True, None
        
        is_consistent, error = self.memory.check_consistency(response, self.current_persona)
        
        if not is_consistent:
            logger.warning(f"Persona consistency check failed: {error}")
        
        return is_consistent, error
    
    def get_persona_context(self) -> str:
        """Get persona context for LLM"""
        if not self.current_persona:
            raise ValueError("No persona selected")
        
        return self.current_persona.to_context_string()
    
    def get_conversation_history(self, count: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        if not self.memory:
            return []
        
        return self.memory.get_recent_messages(count)
    
    def get_typing_delay(self, message_length: int) -> float:
        """Calculate realistic typing delay based on persona"""
        if not self.current_persona:
            return config.persona.typing_delay_seconds
        
        # Calculate based on words per minute
        words = message_length / 5  # Average 5 characters per word
        minutes = words / self.current_persona.max_typing_speed_wpm
        seconds = minutes * 60
        
        # Add some randomness (±20%)
        import random
        variation = random.uniform(0.8, 1.2)
        
        return max(seconds * variation, 1.0)  # Minimum 1 second


# Global persona manager instance
persona_manager = PersonaManager()
