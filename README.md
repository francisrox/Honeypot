# AI Scam Honeypot 🍯🚨

An intelligent honeypot system that detects scam messages, engages scammers with believable AI personas, and extracts fraud infrastructure intelligence.

## 🎯 Features

### ✅ Addresses 12 Critical Drawbacks

1. **False Positives Prevention** - Multi-layer confidence scoring (keyword + pattern + LLM)
2. **AI Persona Consistency** - Locked attributes and conversation memory
3. **Conversation Adaptability** - Handles unexpected turns with fallback strategies
4. **Persona Memory** - Prevents contradictions like "I'm 58" then "just finished college"
5. **Smart Entity Extraction** - Normalizes obfuscated data (e.g., "1234 5678 90" → "123456789")
6. **Scammer Adaptation** - Adaptive strategy phases with suspicion detection
7. **Legal Compliance** - Disclaimers, PII masking, data retention policies
8. **LLM Guardrails** - Strict prompt control prevents helping scammers
9. **Engagement Limits** - Stop conditions (15 msg max, 3+ entities, 30 min)
10. **Infrastructure Resilience** - Rate limiting, fallback handling
11. **Multi-modal Awareness** - Handles voice/image requests with text excuses
12. **Verification Flags** - Marks confidence levels for extracted entities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Incoming Message                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Scam Detector (Multi-Layer)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐          │
│  │ Keywords │→ │ Patterns │→ │ LLM Semantic     │          │
│  │ (30%)    │  │ (30%)    │  │ Analysis (40%)   │          │
│  └──────────┘  └──────────┘  └──────────────────┘          │
│                     │                                        │
│                     ▼                                        │
│           Confidence Score (0.0-1.0)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴──────────┐
         │                      │
         ▼                      ▼
    Not Scam              Scam Detected
    (< 0.85)              (≥ 0.85)
         │                      │
         │                      ▼
         │         ┌────────────────────────────┐
         │         │   Persona Manager          │
         │         │  (Select appropriate       │
         │         │   vulnerable persona)      │
         │         └────────────┬───────────────┘
         │                      │
         │                      ▼
         │         ┌────────────────────────────┐
         │         │   Strategy Engine          │
         │         │  Phase 1: Build Trust      │
         │         │  Phase 2: Extract Intel    │
         │         │  Phase 3: Delay & Probe    │
         │         │  Phase 4: Exit             │
         │         └────────────┬───────────────┘
         │                      │
         │                      ▼
         │         ┌────────────────────────────┐
         │         │   Conversation Loop        │
         │         │  ┌──────────────────────┐  │
         │         │  │ Generate Response    │  │
         │         │  │ Extract Entities     │  │
         │         │  │ Check Stop Conditions│  │
         │         │  └──────────────────────┘  │
         │         └────────────┬───────────────┘
         │                      │
         │                      ▼
         │         ┌────────────────────────────┐
         │         │   Report Generator         │
         │         │  - Extracted entities      │
         │         │  - Conversation transcript │
         │         │  - Strategic analysis      │
         │         │  - Legal disclaimer        │
         │         └────────────────────────────┘
         │
         └──────────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- API key for LLM provider (OpenAI, Gemini, or local Ollama)

### Setup

```bash
# Clone or navigate to the project directory
cd honeypot

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env and add your API key
# LLM_API_KEY=your_api_key_here
```

## 🚀 Usage

### Interactive Demo Mode

```bash
python main.py --demo
```

This starts an interactive session where you can paste scam messages and see the honeypot in action.

### Process Single Message

```bash
python main.py "Congratulations! You won 25 lakh rupees. Pay 5000 processing fee to claim."
```

### Test with Mock Scammer

```bash
python mock_scammer.py
```

This runs automated tests against all scam types (job, investment, banking, prize).

## ⚙️ Configuration

Edit `.env` to customize behavior:

```env
# Scam Detection
CONFIDENCE_THRESHOLD=0.85  # Higher = fewer false positives

# Engagement Limits
MAX_MESSAGES=15
MAX_DURATION_MINUTES=30
MIN_ENTITIES_FOR_STOP=3

# LLM Provider
LLM_PROVIDER=openai  # openai, gemini, or ollama
LLM_MODEL=gpt-4
LLM_API_KEY=your_key_here
```

## 📊 How It Works

### 1. Scam Detection (Multi-Layer)

**Layer 1: Keywords** (30% weight)
- Urgency: "urgent", "immediately", "act now"
- Money: "payment", "transfer", "₹", "lakh"
- Threats: "blocked", "suspended", "arrest"

**Layer 2: Patterns** (30% weight)
- Phone numbers, bank accounts, UPI IDs
- Suspicious URLs (bit.ly, free domains)
- Multiple payment methods

**Layer 3: LLM Semantic Analysis** (40% weight)
- Contextual understanding
- Intent classification
- Confidence scoring

**Final Score** = (0.3 × keyword_score) + (0.3 × pattern_score) + (0.4 × llm_score)

### 2. Persona Selection

Matches persona to scam type:
- **Job Scam** → Job Seeker (24, desperate for work)
- **Investment Scam** → Investor (42, greedy, FOMO)
- **Banking Fraud** → Tech Novice (35, easily confused)
- **Prize/Lottery** → Elderly (68, trusting, lonely)

Each persona has:
- Locked attributes (age, location, occupation)
- Conversation memory (prevents contradictions)
- Behavioral constraints (typing speed, tech knowledge)

### 3. Adaptive Strategy

**Phase 1: Build Trust** (Messages 1-3)
- Show interest and excitement
- Ask clarifying questions
- Establish rapport

**Phase 2: Extract Intel** (Messages 4-8)
- Request payment details
- Ask "how do I proceed?"
- Express readiness to act

**Phase 3: Delay & Probe** (Messages 9+)
- Express small concerns
- Ask for verification
- Extract more information

**Phase 4: Exit** (When limits reached)
- Graceful exit message
- Generate intelligence report

### 4. Stop Conditions

Conversation stops when:
- ✅ Max messages reached (15)
- ✅ Time limit exceeded (30 minutes)
- ✅ Sufficient entities extracted (3+)
- ✅ Scammer shows suspicion (2+ indicators)
- ✅ Conversation unproductive (repetitive)

### 5. Entity Extraction

**Extracted Entities:**
- Bank accounts (normalized: "1234 5678 90" → "123456789")
- UPI IDs (deobfuscated: "fraud(at)upi" → "fraud@upi")
- Phone numbers (international formats)
- URLs (expanded from shorteners)
- Cryptocurrency addresses

**Confidence Levels:**
- `HIGH` - Explicitly provided by scammer
- `MEDIUM` - Extracted from context
- `LOW` - Possibly fake data
- `NEEDS_VERIFICATION` - Suspicious patterns (e.g., "1234567890")

## 📄 Generated Reports

Reports include:
- **Scam Classification** (type, confidence, reasoning)
- **Conversation Summary** (duration, message count, persona used)
- **Extracted Intelligence** (entities with verification flags)
- **Conversation Transcript** (full message history)
- **Strategic Analysis** (scammer behavior, stop reason)
- **Legal Disclaimer** (data verification notes, compliance info)

**Export Formats:**
- JSON (`report_<id>.json`)
- Markdown (`report_<id>.md`)

## 🛡️ Drawback Mitigation Strategies

### False Positives (#1)
- **Solution**: Multi-layer detection with 0.85 threshold
- **Whitelist**: Known legitimate senders bypass detection
- **Conservative**: Errs on side of caution

### AI Persona Issues (#2, #4)
- **Solution**: Locked attributes prevent contradictions
- **Memory**: Tracks all persona statements
- **Validation**: Checks new responses against history

### Conversation Collapse (#3)
- **Solution**: Adaptive strategies for unexpected turns
- **Fallbacks**: Pre-written safe responses
- **Multi-modal**: Handles voice/image requests with excuses

### Poor Entity Extraction (#5)
- **Solution**: Smart normalization handles obfuscation
- **Patterns**: Regex + context-aware extraction
- **Deduplication**: Tracks unique entities

### Scammer Adaptation (#6)
- **Solution**: Suspicion detection triggers behavior change
- **Adaptive**: Changes strategy based on scammer's responses
- **Exit**: Graceful stop when detected

### Legal/Ethical (#7)
- **Solution**: Disclaimers in all reports
- **PII Masking**: Logs mask sensitive data
- **Configurable**: Jurisdiction and retention settings

### LLM Limitations (#8)
- **Solution**: Strict prompt guardrails
- **Validation**: Response filtering prevents helping scammer
- **Fallbacks**: Pre-written responses if LLM fails

### Over-Engagement (#9)
- **Solution**: Multiple stop conditions
- **Limits**: 15 messages, 30 minutes, 3+ entities
- **Efficiency**: Stops when intelligence gathered

### Fake Intelligence (#12)
- **Solution**: Verification flags on all entities
- **Detection**: Identifies sequential/repeated digits
- **Transparency**: Reports mark confidence levels

## ⚠️ Legal Considerations

> **WARNING**: This system engages in cyber deception. Before production use:
> 
> - ✅ Ensure compliance with local cyber laws
> - ✅ Coordinate with law enforcement if applicable
> - ✅ Implement proper data handling policies
> - ✅ Add jurisdiction-specific disclaimers
> - ✅ Consult legal counsel

**For Hackathons/Research**: Safe to use for demonstration and analysis.

**For Production**: Requires legal framework and compliance review.

## 🧪 Testing

### Unit Tests (To be implemented)

```bash
pytest tests/test_scam_detector.py -v
pytest tests/test_persona_manager.py -v
pytest tests/test_entity_extractor.py -v
```

### Integration Tests

```bash
python mock_scammer.py
```

### Manual Testing

1. Run demo mode: `python main.py --demo`
2. Test legitimate messages (should NOT activate)
3. Test scam messages (should activate with correct persona)
4. Verify entity extraction in reports
5. Check persona consistency in transcripts

## 📁 Project Structure

```
honeypot/
├── config.py              # Configuration management
├── utils.py               # Utilities (logging, PII masking, normalization)
├── llm_interface.py       # LLM interface with prompt control
├── scam_detector.py       # Multi-layer scam detection
├── persona_manager.py     # Persona profiles and consistency
├── strategy_engine.py     # Adaptive conversation strategies
├── entity_extractor.py    # Entity extraction and normalization
├── conversation_agent.py  # Response generation orchestration
├── report_generator.py    # Intelligence report generation
├── main.py                # Main system orchestration
├── mock_scammer.py        # Testing utility
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
└── README.md              # This file
```

## 🎓 Example Output

```
============================================================
Processing new message
============================================================
Step 1: Scam Detection
Detection: is_scam=True, confidence=0.92, type=job_scam

Step 2: Activating Honeypot
Persona activated: Priya Sharma (job_seeker)

Step 3: Starting Conversation Loop
👤 Victim: This sounds interesting! What kind of work is it?

🚨 Scammer: Data entry work from home. Very easy!

👤 Victim: That's great! How do I apply?

🚨 Scammer: Just pay ₹2000 registration fee to 9876543210

👤 Victim: Okay, is this UPI or bank account?

🛑 Stopping: sufficient_entities_extracted

Step 4: Generating Intelligence Report
============================================================
Report ID: a3f7c9e2b1d4
Entities extracted: 2 (phone: +919876543210, amount: ₹2000)
============================================================
```

## 🤝 Contributing

This is a hackathon/research project. Contributions welcome for:
- Additional scam type detection
- More persona profiles
- Improved entity extraction patterns
- Better LLM prompts
- Test coverage

## 📜 License

MIT License - Use responsibly and ethically.

## 🙏 Acknowledgments

Built to address the 12 critical drawbacks identified in honeypot systems:
false positives, AI consistency, conversation handling, entity extraction,
legal compliance, LLM limitations, engagement limits, scammer adaptation,
infrastructure resilience, detection avoidance, and data verification.

---

**Remember**: This is a data collection tool, not a scam prevention tool. 
Even partial data is valuable. Use responsibly. 🍯🔒
