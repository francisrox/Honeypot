"""
Conversation Agent with Context-Aware Response Generation
Addresses Drawback #8: LLM Limitations
"""

import time
from typing import Dict, Any, Optional
from utils import logger
from llm_interface import llm
from persona_manager import persona_manager
from strategy_engine import strategy
from entity_extractor import extractor
from config import config


class ConversationAgent:
    """Generates context-aware victim responses"""
    
    def __init__(self):
        self.conversation_active = False
    
    def generate_response(self, scammer_message: str) -> Optional[str]:
        """Generate victim response to scammer's message"""
        
        # Extract entities from scammer's message
        entities = extractor.extract(scammer_message, role="scammer")
        if entities:
            logger.info(f"Extracted {len(entities)} entities from scammer message")
        
        # Analyze scammer's message for strategy
        strategy.analyze_scammer_message(scammer_message)
        
        # Check stop conditions
        should_stop, stop_reason = strategy.should_stop()
        if should_stop:
            logger.info(f"Stopping conversation: {stop_reason.value}")
            return self._generate_exit_message()
        
        # Get strategy guidance
        strategy_guidance = strategy.get_strategy_guidance()
        
        # Get adaptive prompt additions
        adaptive_prompt = strategy.get_adaptive_prompt_addition(scammer_message)
        
        # Build full prompt for LLM
        persona_context = persona_manager.get_persona_context()
        conversation_history = persona_manager.get_conversation_history()
        
        # Generate response
        response_obj = llm.generate_victim_response(
            persona_context=persona_context + adaptive_prompt,
            conversation_history=conversation_history,
            scammer_message=scammer_message
        )
        
        if not response_obj.success:
            logger.error("LLM failed to generate response")
            return None
        
        response = response_obj.content
        
        # Validate persona consistency
        is_consistent, error = persona_manager.validate_response(response)
        if not is_consistent:
            logger.warning(f"Response failed consistency check: {error}")
            # Try one more time with explicit consistency reminder
            retry_prompt = f"{persona_context}\n\nIMPORTANT: Your previous response was inconsistent. Remember your persona details and stay consistent."
            response_obj = llm.generate_victim_response(
                persona_context=retry_prompt,
                conversation_history=conversation_history,
                scammer_message=scammer_message
            )
            response = response_obj.content if response_obj.success else "I'm not sure what you mean."
        
        # Add to conversation memory
        persona_manager.add_message("scammer", scammer_message)
        persona_manager.add_message("victim", response)
        
        # Increment message counter
        strategy.increment_message_count()
        
        # Simulate typing delay
        typing_delay = persona_manager.get_typing_delay(len(response))
        logger.debug(f"Simulating typing delay: {typing_delay:.2f}s")
        time.sleep(min(typing_delay, 5.0))  # Cap at 5 seconds
        
        return response
    
    def _generate_exit_message(self) -> str:
        """Generate graceful exit message"""
        exit_messages = [
            "Thank you for the information. I need to think about this and discuss with my family.",
            "I appreciate your help. Let me check with my bank first and get back to you.",
            "This sounds good, but I need some time to arrange the money. I'll contact you later.",
            "I'm interested, but I need to go now. Can we continue this tomorrow?",
            "Let me talk to my son/daughter about this first. I'll message you back.",
        ]
        
        import random
        return random.choice(exit_messages)
    
    def start_conversation(self, scam_type):
        """Initialize conversation with appropriate persona"""
        persona = persona_manager.select_persona(scam_type)
        self.conversation_active = True
        logger.info(f"Started conversation with persona: {persona.name}")
        return persona
    
    
    def add_message(self, role: str, message: str):
        """Add a message to conversation history (for multi-turn conversations)"""
        persona_manager.add_message(role, message)
    
    def end_conversation(self):
        """End conversation"""
        self.conversation_active = False
        logger.info("Conversation ended")


# Global conversation agent instance
agent = ConversationAgent()
