"""
Intelligence Report Generator
Generates structured reports with legal disclaimers
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from utils import logger, get_timestamp
from config import config
from scam_detector import ScamDetectionResult
from entity_extractor import extractor
from persona_manager import persona_manager
from strategy_engine import strategy


class ReportGenerator:
    """Generates intelligence reports from honeypot conversations"""
    
    def generate_report(self, 
                       detection_result: ScamDetectionResult,
                       stop_reason: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive intelligence report"""
        
        logger.info("Generating intelligence report")
        
        # Get conversation data
        conversation_history = persona_manager.get_conversation_history(count=100)  # All messages
        state_summary = strategy.get_state_summary()
        entities_data = extractor.to_dict()
        
        # Build report
        report = {
            "report_metadata": self._get_metadata(),
            "scam_classification": self._get_classification(detection_result),
            "conversation_summary": self._get_conversation_summary(conversation_history, state_summary),
            "extracted_intelligence": entities_data,
            "conversation_transcript": self._get_transcript(conversation_history),
            "strategic_analysis": self._get_strategic_analysis(state_summary, stop_reason),
            "legal_disclaimer": self._get_legal_disclaimer() if config.legal.enable_legal_disclaimers else None
        }
        
        return report
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get report metadata"""
        return {
            "report_id": self._generate_report_id(),
            "generated_at": get_timestamp(),
            "honeypot_version": "1.0.0",
            "jurisdiction": config.legal.jurisdiction
        }
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        import hashlib
        timestamp = datetime.utcnow().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _get_classification(self, detection_result: ScamDetectionResult) -> Dict[str, Any]:
        """Get scam classification details"""
        return {
            "is_scam": detection_result.is_scam,
            "confidence": detection_result.confidence,
            "scam_type": detection_result.scam_type.value,
            "reasoning": detection_result.reasoning,
            "detection_layers": detection_result.layer_scores
        }
    
    def _get_conversation_summary(self, history: list, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "total_messages": len(history),
            "duration_minutes": state.get("elapsed_minutes", 0),
            "conversation_phases": self._extract_phases(history),
            "persona_used": persona_manager.current_persona.name if persona_manager.current_persona else "Unknown"
        }
    
    def _extract_phases(self, history: list) -> list:
        """Extract conversation phases from history"""
        # Simplified - in production, analyze message content
        phases = []
        if len(history) > 0:
            phases.append("Initial contact")
        if len(history) > 3:
            phases.append("Trust building")
        if len(history) > 6:
            phases.append("Intelligence extraction")
        return phases
    
    def _get_transcript(self, history: list) -> list:
        """Get formatted conversation transcript"""
        transcript = []
        for msg in history:
            transcript.append({
                "timestamp": msg.get("timestamp", ""),
                "role": msg.get("role", ""),
                "message": msg.get("content", "")
            })
        return transcript
    
    def _get_strategic_analysis(self, state: Dict[str, Any], stop_reason: Optional[str]) -> Dict[str, Any]:
        """Get strategic analysis"""
        return {
            "final_phase": state.get("current_phase", "unknown"),
            "stop_reason": stop_reason,
            "entities_extracted": state.get("entities_extracted", 0),
            "suspicion_indicators_detected": state.get("suspicion_indicators", 0),
            "scammer_behavior": self._analyze_scammer_behavior(state)
        }
    
    def _analyze_scammer_behavior(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scammer's behavior patterns"""
        return {
            "repetitive_messages": state.get("scammer_repetitions", 0) > 2,
            "showed_suspicion": state.get("suspicion_indicators", 0) > 0,
            "engagement_level": "high" if state.get("message_count", 0) > 10 else "medium"
        }
    
    def _get_legal_disclaimer(self) -> str:
        """Get legal disclaimer"""
        return """
LEGAL DISCLAIMER:

This report was generated by an automated honeypot system for cybersecurity research and scam detection purposes.

IMPORTANT NOTICES:
1. Data Verification: All extracted entities should be independently verified before use. Some data may be fake, temporary, or test accounts used by scammers.

2. Legal Use: This report is intended for:
   - Cybersecurity research
   - Law enforcement coordination (where applicable)
   - Scam pattern analysis
   - Educational purposes

3. Privacy Considerations: This system engaged in cyber deception. Ensure compliance with local laws regarding:
   - Honeypot operations
   - Data collection and retention
   - Evidence handling

4. No Warranty: The information is provided "as is" without warranty. The system may produce false positives or miss scam indicators.

5. Jurisdiction: This report was generated under the jurisdiction of {jurisdiction}. Consult legal counsel before using this data for law enforcement or legal proceedings.

6. Data Retention: Per configuration, conversation data will be retained for {retention_days} days.

For questions or to report issues, contact the system administrator.
""".format(
            jurisdiction=config.legal.jurisdiction,
            retention_days=config.legal.data_retention_days
        )
    
    def export_json(self, report: Dict[str, Any], filepath: str):
        """Export report as JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
    
    def export_markdown(self, report: Dict[str, Any], filepath: str):
        """Export report as Markdown"""
        try:
            md_content = self._format_as_markdown(report)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"Report exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
    
    def _format_as_markdown(self, report: Dict[str, Any]) -> str:
        """Format report as Markdown"""
        md = f"""# Honeypot Intelligence Report

**Report ID:** {report['report_metadata']['report_id']}  
**Generated:** {report['report_metadata']['generated_at']}  
**Jurisdiction:** {report['report_metadata']['jurisdiction']}

---

## Scam Classification

- **Is Scam:** {report['scam_classification']['is_scam']}
- **Confidence:** {report['scam_classification']['confidence']:.2%}
- **Scam Type:** {report['scam_classification']['scam_type']}
- **Reasoning:** {report['scam_classification']['reasoning']}

## Conversation Summary

- **Total Messages:** {report['conversation_summary']['total_messages']}
- **Duration:** {report['conversation_summary']['duration_minutes']:.2f} minutes
- **Persona Used:** {report['conversation_summary']['persona_used']}

## Extracted Intelligence

**Total Entities:** {report['extracted_intelligence']['total_entities']}  
**High-Value Entities:** {report['extracted_intelligence']['high_value_entities']}

### Entities by Type
"""
        
        for entity_type, count in report['extracted_intelligence']['entities_by_type'].items():
            md += f"- **{entity_type}:** {count}\n"
        
        md += "\n### Detailed Entities\n\n"
        for entity in report['extracted_intelligence']['all_entities']:
            md += f"- **{entity['type']}:** `{entity['normalized_value']}` (confidence: {entity['confidence']})\n"
        
        md += f"\n## Strategic Analysis\n\n"
        md += f"- **Final Phase:** {report['strategic_analysis']['final_phase']}\n"
        md += f"- **Stop Reason:** {report['strategic_analysis']['stop_reason']}\n"
        md += f"- **Entities Extracted:** {report['strategic_analysis']['entities_extracted']}\n"
        
        md += "\n## Conversation Transcript\n\n"
        for msg in report['conversation_transcript']:
            role = "🚨 Scammer" if msg['role'] == 'scammer' else "👤 Victim"
            md += f"**{role}:** {msg['message']}\n\n"
        
        if report.get('legal_disclaimer'):
            md += f"\n---\n\n{report['legal_disclaimer']}\n"
        
        return md


# Global report generator instance
report_gen = ReportGenerator()
