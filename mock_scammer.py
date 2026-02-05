"""
Mock Scammer for Testing
Simulates various scam types for testing the honeypot
"""

import sys
import random
from typing import List, Dict, Optional
from scam_detector import ScamType


class MockScammer:
    """Simulates scammer behavior for testing"""
    
    SCAM_SCRIPTS = {
        ScamType.JOB_SCAM: [
            "Congratulations! You have been selected for a work from home opportunity. Earn ₹25,000 per month. Registration fee: ₹2,000. Interested?",
            "Yes! This is a genuine opportunity with our company. You just need to pay a small training fee of ₹2,000.",
            "Send the payment to this account: 9876543210. Bank: HDMI Bank. Name: Rajesh Kumar.",
            "After payment, we will send you the training materials and your first assignment.",
        ],
        
        ScamType.INVESTMENT_SCAM: [
            "URGENT INVESTMENT OPPORTUNITY! Invest ₹10,000 and get ₹50,000 in 30 days. 500% returns guaranteed!",
            "This is a limited time offer. Only 10 spots left. Send money to secure your spot now!",
            "Transfer to UPI: invest@paytm or account number 1234567890123.",
            "Many people have already made lakhs. Don't miss this chance!",
        ],
        
        ScamType.BANKING_FRAUD: [
            "ALERT: Your bank account will be BLOCKED in 24 hours due to suspicious activity. Verify immediately!",
            "Click this link to verify: bit.ly/verify123 or call us at +91-9876543210",
            "You need to update your KYC details. Share your account number and OTP to verify.",
            "If you don't verify, your account will be permanently frozen and money will be lost.",
        ],
        
        ScamType.PRIZE_LOTTERY: [
            "CONGRATULATIONS! You have WON ₹25 LAKH in the Lucky Draw! Claim now!",
            "To claim your prize, you need to pay processing fee of ₹5,000.",
            "Send payment to: 9988776655 (PhonePe/GPay). After payment, prize will be transferred.",
            "This is a limited time offer. Claim within 24 hours or prize will go to next winner!",
        ],
    }
    
    def __init__(self, scam_type: ScamType):
        self.scam_type = scam_type
        self.script = self.SCAM_SCRIPTS.get(scam_type, [])
        self.message_index = 0
        self.suspicious = False
    
    def get_next_message(self, victim_response: str = "") -> str:
        """Get next message from scammer"""
        
        # Analyze victim response for suspicion triggers
        if victim_response:
            self._analyze_victim_response(victim_response)
        
        # If suspicious, change behavior
        if self.suspicious:
            return random.choice([
                "Are you real? Send me a voice message.",
                "Why are you asking so many questions?",
                "This is taking too long. Never mind.",
            ])
        
        # Get next scripted message
        if self.message_index < len(self.script):
            message = self.script[self.message_index]
            self.message_index += 1
            return message
        else:
            # Script exhausted, repeat last message or end
            return random.choice([
                "So are you interested or not?",
                "Please send the payment soon.",
                "Let me know if you want to proceed.",
            ])
    
    def _analyze_victim_response(self, response: str):
        """Analyze victim response for suspicion indicators"""
        
        # Scammer gets suspicious if victim asks too many questions
        question_count = response.count('?')
        if question_count >= 3:
            self.suspicious = True
        
        # Suspicious keywords
        suspicious_keywords = ['verify', 'proof', 'documentation', 'legal', 'police']
        if any(kw in response.lower() for kw in suspicious_keywords):
            self.suspicious = True


def run_mock_conversation(scam_type: ScamType):
    """Run a mock conversation for testing"""
    from main import HoneypotSystem
    
    print(f"\n{'='*60}")
    print(f"MOCK SCAM TEST: {scam_type.value}")
    print(f"{'='*60}\n")
    
    # Initialize honeypot
    honeypot = HoneypotSystem()
    
    # Initialize mock scammer
    scammer = MockScammer(scam_type)
    
    # Get initial scam message
    initial_message = scammer.get_next_message()
    print(f"🚨 [SCAMMER]: {initial_message}\n")
    
    # Define scammer callback for multi-turn conversation
    def scammer_callback(victim_response: str) -> Optional[str]:
        """Callback function that returns scammer's next message"""
        if scammer.suspicious:
            # Scammer is suspicious, might end conversation
            if scammer.message_index > 2:  # End if already had a few exchanges
                print(f"[INFO] Scammer became suspicious and ended conversation\n")
                return None
        
        next_message = scammer.get_next_message(victim_response)
        if next_message:
            print(f"🚨 [SCAMMER]: {next_message}\n")
        return next_message
    
    # Process through honeypot with callback
    result = honeypot.process_message(
        initial_message, 
        scammer_callback=scammer_callback
    )
    
    if not result['honeypot_activated']:
        print("❌ [FAIL] Honeypot did NOT activate (false negative!)\n")
        return
    
    print(f"✅ [SUCCESS] Honeypot activated!")
    print(f"Scam Type Detected: {result['detection_result']['scam_type']}")
    print(f"Confidence: {result['detection_result']['confidence']:.2%}\n")
    
    # Display conversation summary
    print(f"{'='*60}")
    print("CONVERSATION SUMMARY")
    print(f"{'='*60}")
    print(f"Messages Exchanged: {result['conversation_results']['messages_exchanged']}")
    print(f"Stop Reason: {result['conversation_results']['stop_reason']}")
    print(f"\nReport Files:")
    print(f"  - JSON: {result['report_files']['json']}")
    print(f"  - Markdown: {result['report_files']['markdown']}")
    
    # Display extracted entities
    entities = result['report']['extracted_intelligence']
    print(f"\nEntities Extracted: {entities['high_value_entities']}")
    print(f"Entity Types: {entities['entities_by_type']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Test all scam types
    for scam_type in [ScamType.JOB_SCAM, ScamType.INVESTMENT_SCAM, 
                      ScamType.BANKING_FRAUD, ScamType.PRIZE_LOTTERY]:
        run_mock_conversation(scam_type)
        print("\n" + "="*80 + "\n")
