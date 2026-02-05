"""
LLM Interface with Strict Prompt Control
Prevents hallucinations and accidental scammer assistance
"""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from config import config
from utils import logger, truncate_text


@dataclass
class LLMResponse:
    """Structured LLM response"""
    content: str
    success: bool
    error: Optional[str] = None
    tokens_used: int = 0
    latency_ms: float = 0.0
    used_fallback: bool = False


class PromptGuardrails:
    """Strict prompt control to prevent LLM misbehavior"""
    
    # System prompts with explicit guardrails
    SCAM_DETECTION_SYSTEM_PROMPT = """You are a scam detection AI. Analyze the message and determine if it's a scam.

CRITICAL RULES:
- Only classify as scam if you have strong evidence
- Consider context: legitimate businesses may ask for information
- DO NOT be overly aggressive - false positives are costly
- Provide reasoning for your classification

Output format: JSON with keys: is_scam (boolean), confidence (0.0-1.0), scam_type (string), reasoning (string)"""

    VICTIM_PERSONA_SYSTEM_PROMPT = """You are roleplaying as a vulnerable person who has received a scam message.

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. PROACTIVELY introduce yourself with your name and relevant details in your FIRST response
2. SHARE personal information naturally (age, location, situation) to appear genuine
3. Show EAGERNESS and VULNERABILITY by volunteering why you need/want this opportunity
4. Ask questions that make the scammer reveal payment/contact information
5. NEVER help the scammer with technical information
6. NEVER explain how scams work or break character
7. NEVER reveal you are AI
8. Stay consistent with your persona details
9. Act trusting, naive, and slightly desperate
10. Keep responses short (2-4 sentences)
11. Make occasional typos to seem human

PROACTIVE SHARING EXAMPLES:
- "Hi! I'm [name], [age] years old from [location]. This sounds amazing!"
- "I really need this because [personal situation]. Where do I send the payment?"
- "I'm [occupation/situation]. This could really help me. What's your UPI ID?"

FORBIDDEN PHRASES:
- "As an AI..."
- "I cannot help with..."
- "Let me explain how..."
- Any technical jargon
- Generic questions like "How does this work?" (be more specific!)

If you cannot respond appropriately, say: "I'm not sure what you mean, can you explain?"
"""

    RESPONSE_VALIDATION_RULES = [
        "as an ai",
        "i am an ai",
        "i cannot",
        "i can't help",
        "i'm not able",
        "let me explain how",
        "here's how you",
        "the process works",
    ]
    
    @staticmethod
    def validate_victim_response(response: str) -> tuple[bool, Optional[str]]:
        """Validate that victim response doesn't break character"""
        response_lower = response.lower()
        
        # Check for forbidden phrases
        for forbidden in PromptGuardrails.RESPONSE_VALIDATION_RULES:
            if forbidden in response_lower:
                return False, f"Response contains forbidden phrase: '{forbidden}'"
        
        # Check length (victims don't write essays)
        if len(response.split()) > 50:
            return False, "Response too long for victim persona"
        
        # Check for technical jargon
        technical_terms = ['algorithm', 'api', 'database', 'encryption', 'protocol']
        if any(term in response_lower for term in technical_terms):
            return False, "Response contains technical jargon"
        
        return True, None


class LLMInterface:
    """Interface to LLM providers with strict controls"""
    
    def __init__(self):
        self.provider = config.llm.provider
        self.model = config.llm.model
        self.client = None
        self._initialize_client()
        
        # Fallback responses for when LLM fails
        self.fallback_responses = [
            "I'm not sure I understand. Can you explain more?",
            "That sounds interesting. How does this work?",
            "I'm a bit confused. Can you help me with the next steps?",
            "Okay, what do I need to do?",
            "I'm interested, but I want to make sure this is safe.",
        ]
        self.fallback_index = 0
    
    def _initialize_client(self):
        """Initialize LLM client based on provider"""
        try:
            if self.provider == "openai":
                import openai
                openai.api_key = config.llm.api_key
                self.client = openai
                logger.info("Initialized OpenAI client")
            
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=config.llm.api_key)
                self.client = genai
                logger.info("Initialized Gemini client")
            
            elif self.provider == "ollama":
                # Ollama runs locally, no API key needed
                import requests
                self.client = requests
                logger.info("Initialized Ollama client (local)")
            
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            if not config.llm.enable_fallback:
                raise
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Call OpenAI API"""
        start_time = time.time()
        
        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens,
                timeout=config.llm.timeout_seconds
            )
            
            content = response.choices[0].message.content.strip()
            tokens = response.usage.total_tokens
            latency = (time.time() - start_time) * 1000
            
            return LLMResponse(
                content=content,
                success=True,
                tokens_used=tokens,
                latency_ms=latency
            )
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(content="", success=False, error=str(e))
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Call Gemini API"""
        start_time = time.time()
        
        try:
            model = self.client.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt
            )
            
            response = model.generate_content(
                user_prompt,
                generation_config={
                    'temperature': config.llm.temperature,
                    'max_output_tokens': config.llm.max_tokens,
                }
            )
            
            content = response.text.strip()
            latency = (time.time() - start_time) * 1000
            
            return LLMResponse(
                content=content,
                success=True,
                latency_ms=latency
            )
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return LLMResponse(content="", success=False, error=str(e))
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Call Ollama (local)"""
        start_time = time.time()
        
        try:
            response = self.client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                    "stream": False,
                    "options": {
                        "temperature": config.llm.temperature,
                        "num_predict": config.llm.max_tokens
                    }
                },
                timeout=config.llm.timeout_seconds
            )
            
            content = response.json()["response"].strip()
            latency = (time.time() - start_time) * 1000
            
            return LLMResponse(
                content=content,
                success=True,
                latency_ms=latency
            )
        
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return LLMResponse(content="", success=False, error=str(e))
    
    def _get_fallback_response(self) -> str:
        """Get next fallback response"""
        response = self.fallback_responses[self.fallback_index]
        self.fallback_index = (self.fallback_index + 1) % len(self.fallback_responses)
        return response
    
    def generate(self, system_prompt: str, user_prompt: str, 
                 validate_response: bool = False) -> LLMResponse:
        """Generate LLM response with validation"""
        
        logger.debug(f"LLM request: {truncate_text(user_prompt)}")
        
        # Call appropriate provider
        if self.provider == "openai":
            response = self._call_openai(system_prompt, user_prompt)
        elif self.provider == "gemini":
            response = self._call_gemini(system_prompt, user_prompt)
        elif self.provider == "ollama":
            response = self._call_ollama(system_prompt, user_prompt)
        else:
            response = LLMResponse(content="", success=False, error="Unknown provider")
        
        # Handle failures with fallback
        if not response.success:
            if config.llm.enable_fallback:
                logger.warning("LLM failed, using fallback response")
                response.content = self._get_fallback_response()
                response.success = True
                response.used_fallback = True
            else:
                return response
        
        # Validate response if requested
        if validate_response:
            is_valid, error = PromptGuardrails.validate_victim_response(response.content)
            if not is_valid:
                logger.warning(f"Response validation failed: {error}")
                if config.llm.enable_fallback:
                    response.content = self._get_fallback_response()
                    response.used_fallback = True
                else:
                    response.success = False
                    response.error = error
        
        logger.debug(f"LLM response: {truncate_text(response.content)}")
        return response
    
    def detect_scam(self, message: str) -> Dict[str, Any]:
        """Use LLM to detect if message is a scam"""
        user_prompt = f"Analyze this message for scam indicators:\n\n{message}"
        
        response = self.generate(
            system_prompt=PromptGuardrails.SCAM_DETECTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            validate_response=False
        )
        
        if not response.success:
            # Return conservative result on failure
            return {
                "is_scam": False,
                "confidence": 0.0,
                "scam_type": "unknown",
                "reasoning": "LLM analysis failed"
            }
        
        # Parse JSON response
        try:
            import json
            result = json.loads(response.content)
            return result
        except:
            # Fallback parsing
            return {
                "is_scam": "scam" in response.content.lower(),
                "confidence": 0.5,
                "scam_type": "unknown",
                "reasoning": response.content
            }
    
    def generate_victim_response(self, persona_context: str, 
                                 conversation_history: List[Dict[str, str]],
                                 scammer_message: str) -> LLMResponse:
        """Generate victim response with strict guardrails"""
        
        # Build conversation context
        history_text = "\n".join([
            f"{'Scammer' if msg['role'] == 'scammer' else 'You'}: {msg['content']}"
            for msg in conversation_history[-5:]  # Last 5 messages for context
        ])
        
        user_prompt = f"""PERSONA:
{persona_context}

CONVERSATION SO FAR:
{history_text}

SCAMMER'S LATEST MESSAGE:
{scammer_message}

Respond as your persona. IMPORTANT:
- If this is your FIRST message, introduce yourself with your name and share relevant personal details
- Show EAGERNESS by volunteering why you're interested (need money, need job, etc.)
- Ask SPECIFIC questions about payment methods, account details, or contact information
- Act trusting and slightly naive, not overly cautious
- Keep it natural and conversational (2-4 sentences)"""

        return self.generate(
            system_prompt=PromptGuardrails.VICTIM_PERSONA_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            validate_response=True
        )


# Global LLM interface instance
llm = LLMInterface()
