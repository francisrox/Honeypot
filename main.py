"""
Main Honeypot System
Orchestrates the entire workflow
"""

import sys
from typing import Optional
from utils import logger
from config import config
from scam_detector import detector
from conversation_agent import agent
from report_generator import report_gen
from strategy_engine import StopReason


class HoneypotSystem:
    """Main honeypot orchestration system"""
    
    def __init__(self):
        self.initialized = False
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration"""
        is_valid, error = config.validate()
        if not is_valid:
            logger.error(f"Configuration validation failed: {error}")
            raise ValueError(f"Invalid configuration: {error}")
        
        logger.info("Configuration validated successfully")
        logger.info(f"LLM Provider: {config.llm.provider}")
        logger.info(f"Confidence Threshold: {config.scam_detection.confidence_threshold}")
        logger.info(f"Max Messages: {config.engagement.max_messages}")
        self.initialized = True
    
    def process_message(self, message: str, sender: Optional[str] = None, scammer_callback=None) -> dict:
        """
        Process incoming message through honeypot pipeline
        
        Args:
            message: The message to analyze
            sender: Optional sender identifier
            scammer_callback: Optional callback function for multi-turn conversations
        
        Returns:
            Dictionary with processing results
        """
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        logger.info("="*60)
        logger.info("Processing new message")
        logger.info("="*60)
        
        # Step 1: Scam Detection
        logger.info("Step 1: Scam Detection")
        detection_result = detector.detect(message, sender)
        
        logger.info(f"Detection: is_scam={detection_result.is_scam}, "
                   f"confidence={detection_result.confidence:.2f}, "
                   f"type={detection_result.scam_type.value}")
        
        # If not a scam, return early
        if not detection_result.is_scam:
            logger.info("Message classified as legitimate. Honeypot NOT activated.")
            return {
                "honeypot_activated": False,
                "detection_result": detection_result.to_dict(),
                "message": "Message appears legitimate"
            }
        
        # Step 2: Activate Honeypot
        logger.info("Step 2: Activating Honeypot")
        logger.info(f"Scam detected with {detection_result.confidence:.2%} confidence")
        
        # Start conversation with appropriate persona
        persona = agent.start_conversation(detection_result.scam_type)
        logger.info(f"Persona activated: {persona.name}")
        
        # Step 3: Conversation Loop
        logger.info("Step 3: Starting Conversation Loop")
        
        conversation_results = self._conversation_loop(message, scammer_callback)
        
        # Step 4: Generate Report
        logger.info("Step 4: Generating Intelligence Report")
        report = report_gen.generate_report(
            detection_result=detection_result,
            stop_reason=conversation_results.get("stop_reason")
        )
        
        # Export report
        report_id = report['report_metadata']['report_id']
        report_gen.export_json(report, f"report_{report_id}.json")
        report_gen.export_markdown(report, f"report_{report_id}.md")
        
        logger.info("="*60)
        logger.info("Honeypot processing complete")
        logger.info(f"Report ID: {report_id}")
        logger.info(f"Entities extracted: {report['extracted_intelligence']['high_value_entities']}")
        logger.info("="*60)
        
        return {
            "honeypot_activated": True,
            "detection_result": detection_result.to_dict(),
            "conversation_results": conversation_results,
            "report": report,
            "report_files": {
                "json": f"report_{report_id}.json",
                "markdown": f"report_{report_id}.md"
            }
        }
    
    def _conversation_loop(self, initial_message: str, scammer_callback=None) -> dict:
        """
        Run conversation loop with scammer.
        
        Args:
            initial_message: The first message from the scammer.
            scammer_callback: A function that takes the victim's response and returns the scammer's next message.
                              If None, it simulates a single turn or waits for manual input in interactive mode.
        
        Returns:
            Dictionary with conversation results.
        """
        messages_exchanged = 0
        stop_reason = StopReason.MAX_MESSAGES  # Default stop reason

        # Generate first response
        victim_response = agent.generate_response(initial_message)
        messages_exchanged += 1
        
        if victim_response:
            logger.info(f"Victim: {victim_response}")
            if scammer_callback is None:
                print(f"\nVictim: {victim_response}\n") # For interactive demo
        
        # If no scammer callback, we assume a single turn for now (e.g., for initial testing)
        if scammer_callback is None:
            return {
                "messages_exchanged": messages_exchanged,
                "stop_reason": StopReason.DEMO_MODE.value,
                "last_victim_response": victim_response
            }

        # Multi-turn conversation loop
        while messages_exchanged < config.engagement.max_messages:
            scammer_message = scammer_callback(victim_response)
            if scammer_message is None: # Scammer callback indicates end of conversation
                stop_reason = StopReason.SCAMMER_DISENGAGED
                break
            
            logger.info(f"Scammer: {scammer_message}")
            agent.add_message("scammer", scammer_message) # Add scammer's message to conversation history

            victim_response = agent.generate_response(scammer_message)
            messages_exchanged += 1
            
            if victim_response is None: # Agent decided to stop
                stop_reason = StopReason.AGENT_DISENGAGED
                break
            
            logger.info(f"Victim: {victim_response}")
            
        return {
            "messages_exchanged": messages_exchanged,
            "stop_reason": stop_reason.value,
            "last_victim_response": victim_response
        }
    
    def run_interactive_demo(self):
        """Run interactive demo mode"""
        print("="*60)
        print("AI SCAM HONEYPOT - INTERACTIVE DEMO")
        print("="*60)
        print(f"Confidence Threshold: {config.scam_detection.confidence_threshold}")
        print(f"Max Messages: {config.engagement.max_messages}")
        print(f"LLM Provider: {config.llm.provider}")
        print("="*60)
        print("\nEnter a message to analyze (or 'quit' to exit):\n")
        
        while True:
            try:
                message = input("📨 Message: ").strip()
                
                if message.lower() in ['quit', 'exit', 'q']:
                    print("\nExiting demo mode.")
                    break
                
                if not message:
                    continue
                
                # Process message
                result = self.process_message(message)
                
                # Display results
                print("\n" + "="*60)
                print("RESULTS:")
                print("="*60)
                print(f"Honeypot Activated: {result['honeypot_activated']}")
                
                if result['honeypot_activated']:
                    print(f"Scam Type: {result['detection_result']['scam_type']}")
                    print(f"Confidence: {result['detection_result']['confidence']:.2%}")
                    print(f"\nVictim Response: {result['conversation_results']['victim_response']}")
                else:
                    print(f"Classification: Legitimate message")
                
                print("="*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nExiting demo mode.")
                break
            except Exception as e:
                logger.error(f"Error in demo mode: {e}")
                print(f"\nError: {e}\n")


def main():
    """Main entry point"""
    
    # Initialize system
    try:
        honeypot = HoneypotSystem()
    except Exception as e:
        print(f"Failed to initialize honeypot: {e}")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            # Interactive demo mode
            honeypot.run_interactive_demo()
        else:
            # Process single message from command line
            message = " ".join(sys.argv[1:])
            result = honeypot.process_message(message)
            print(f"\nHoneypot Activated: {result['honeypot_activated']}")
            if result['honeypot_activated']:
                print(f"Report: {result['report_files']['markdown']}")
    else:
        # Default: run demo mode
        honeypot.run_interactive_demo()


if __name__ == "__main__":
    main()
