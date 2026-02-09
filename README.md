# AI Toolkit

A comprehensive suite of AI-powered tools for research and artifact review. Features intelligent library management and multimodal artifact critique with Gemini for PDFs, images, videos, audio, and presentations.

## 📦 What's Inside

This toolkit contains two powerful AI agents:

1. **[Library Research Agent](#library-research-agent)** - Curated knowledge library with intelligent web search fallback
2. **[Artifact Critic](#artifact-critic-gemini-multimodal-feedback)** - Gemini-powered multimodal review for PDFs, images, videos, audio, and presentations

## 🗂️ Table of Contents

- [Library Research Agent](#library-research-agent)
  - [Features](#-key-features)
  - [Quick Start](#-quick-start)
  - [Usage](#-usage-examples)
- [Artifact Critic](#artifact-critic-gemini-multimodal-feedback)
  - [Features](#-what-it-does)
  - [Quick Start](#-setup)
  - [Usage](#-basic-usage)
  - [Media Analysis](#media-analysis-with-artifact-critic)
- [Configuration](#configuration)
- [Security](#-security-first)

---

# Library Research Agent

An AI-powered research assistant that maintains a curated knowledge library and intelligently uses web search only when needed. Featured with automatic citation, source quality control, and freshness management.

## 🎯 Key Features

- **Library-First Approach**: Searches internal knowledge base before using web search
- **Automatic Freshness Management**: Tracks content age and refreshes stale information
- **Smart Deduplication**: Prevents duplicate entries by normalizing URLs
- **Citation Required**: All web-derived facts include proper citations
- **Source Quality Control**: Prioritizes reputable sources with credibility tracking
- **Configurable TTL**: Topic-based time-to-live rules for content freshness
- **Cost-Efficient**: Limits web searches to reduce API costs

## 🔒 Security First

- ✅ API keys loaded from environment only (`.env` file)
- ✅ Secrets never logged, printed, or stored in code
- ✅ Automatic secret sanitization in error messages
- ✅ Validation prevents placeholder keys
- ❌ `.env` file excluded from version control

**Never commit secrets to version control!**

## 📋 Requirements

- Python 3.9+
- **OpenAI API key** (for Library Research Agent - GPT-4 with web search)
- **Gemini API key** (for Artifact Critic and Media Analyzer)
- ~50MB disk space for library and media storage

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone git@github.com:jam398/ai_toolkit.git
cd ai_toolkit
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your API keys
# NEVER commit .env to version control!
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
GEMINI_API_KEY=your-actual-gemini-key-here
```

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://aistudio.google.com/apikey

### 3. Run the Agent

**Interactive Mode:**
```bash
python main.py
```

**Single Question:**
```bash
python main.py -q "What is the latest Python version?"
```

**Save Results to File:**
```bash
python main.py -q "Explain async/await in Python" -o results.txt
```

**Check Library Stats:**
```bash
python main.py --stats
```

## 📖 Usage Examples

### Interactive Mode

```
🔍 Question: What are the key features of Python 3.12?

⏳ Researching...

================================================================================
ANSWER
================================================================================
Python 3.12, released in October 2023, includes several major improvements:

1. **Performance**: 5% faster than 3.11 on average
2. **Better Error Messages**: More precise tracebacks with suggestions
3. **Type System Improvements**: PEP 692 (TypedDict with **kwargs)
4. **New f-string Parser**: More flexible and powerful

[Complete formatted answer with citations...]

================================================================================
LIBRARY UPDATES
================================================================================
• ADDED: Python 3.12 Release Notes
  URL: https://docs.python.org/3.12/whatsnew/3.12.html

================================================================================
SOURCES
================================================================================
1. Python 3.12 Release Notes
   URL: https://docs.python.org/3.12/whatsnew/3.12.html
   Publisher: Python.org
   Accessed: 2026-02-06T10:30:00

================================================================================
QUERY STATISTICS
================================================================================
Library searches: 1
Web searches: 1
Library updates: 1
================================================================================
```

### Library-First Behavior

When asking about known topics:

```
🔍 Question: What is async/await in Python?

⏳ Researching...

[Agent finds answer in library - NO web search needed]
Library searches: 1
Web searches: 0  ← No web search!
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│  User Question                                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Library Research Agent (research_agent.py)         │
│  - Query orchestration                              │
│  - Tool selection                                   │
│  - Response formatting                              │
└────────────┬────────────────────────┬────────────────┘
             │                        │
             ▼                        ▼
┌────────────────────────┐  ┌────────────────────────┐
│  Library Store         │  │  OpenAI API            │
│  (library_store.py)    │  │  - GPT-4               │
│  - ChromaDB vectors    │  │  - Web search tool     │
│  - Metadata tracking   │  │  - Function calling    │
│  - Freshness checks    │  └────────────────────────┘
└────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│  Agent Tools (agent_tools.py)                       │
│  - search_library()                                 │
│  - add_to_library()                                 │
│  - get_library_stats()                              │
└─────────────────────────────────────────────────────┘
```

### Workflow

```
1. User asks question
   ↓
2. Agent searches library FIRST
   ↓
3. Check if results are fresh and sufficient
   ↓
   ├─ YES → Answer from library only
   │
   └─ NO → Execute web search (max 3 searches)
           ↓
           Store valuable findings in library
           ↓
           Answer with citations
```

## 📚 Library Entry Schema

Each library entry includes:

```python
{
    "title": "Clear, descriptive title",
    "url": "https://source.com/article",
    "publisher": "Publisher name",
    "date_published": "2024-01-01",  # If available
    "date_accessed": "2026-02-06T10:30:00",  # Auto-tracked
    "topic_tags": ["python", "documentation"],
    "summary": "5-10 bullet point summary...",
    "key_facts": [
        "Fact 1 with citation (https://source.com)",
        "Fact 2 with citation (https://source.com)"
    ],
    "credibility_notes": "Official documentation / Expert source",
    "freshness_ttl_days": 30  # Topic-dependent TTL
}
```

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
OPENAI_MODEL=gpt-4o
LIBRARY_DB_PATH=./library_data
MAX_WEB_SEARCHES_PER_QUERY=3
MAX_SEARCH_RESULTS_PER_SEARCH=5
```

### TTL Rules by Topic

Configured in `config.py`:

```python
TOPIC_TTL_RULES = {
    "news": 7,              # News gets stale quickly
    "current_events": 7,
    "technology": 14,
    "research": 30,
    "documentation": 60,    # Docs stay fresh longer
    "history": 180,
    "reference": 365,
}
```

## 🧪 Testing

Run the acceptance test suite:

```bash
python tests.py
```

**Tests Coverage:**
1. ✅ No-Secret Test: Validates secret sanitization
2. ✅ Library-First Test: Confirms library search before web
3. ✅ Staleness Test: Verifies TTL and refresh logic
4. ✅ Deduplication Test: Prevents duplicate entries
5. ✅ Citation Test: Ensures proper source attribution

## 📁 Project Structure

```
project/
├── .env.example          # Environment template (safe to commit)
├── .env                  # Your actual secrets (NEVER commit)
├── .gitignore           # Excludes .env and sensitive files
├── requirements.txt      # Python dependencies
├── config.py            # Configuration and security
├── library_store.py     # Storage backend with vector search
├── agent_tools.py       # Tool definitions and implementations
├── research_agent.py    # Main agent logic with OpenAI
├── main.py              # CLI application
├── tests.py             # Acceptance tests
└── README.md            # This file

# Generated at runtime:
library_data/            # ChromaDB storage (gitignored)
```

## 🔧 Adding Custom Tools

To add new tool functions:

1. **Define the tool schema** in `agent_tools.py`:

```python
{
    "type": "function",
    "function": {
        "name": "your_tool_name",
        "description": "What the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    }
}
```

2. **Implement the tool** in `AgentTools` class:

```python
def _your_tool_name(self, args: Dict[str, Any]) -> str:
    """Your tool implementation."""
    param1 = args.get("param1")
    # ... your logic ...
    return json.dumps({"result": "..."})
```

3. **Register in execute_tool**:

```python
elif tool_name == "your_tool_name":
    return self._your_tool_name(arguments)
```

## 🎯 Best Practices

### For Users

- **Be Specific**: Clear questions get better answers
- **Use Commands**: Type `stats` to see library status
- **Check Sources**: Always review citations for important decisions
- **Trust Fresh Data**: Library entries show freshness status

### For Developers

- **Never log secrets**: Always use `sanitize_for_logging()`
- **Test regularly**: Run `python tests.py` after changes
- **Update TTL rules**: Adjust based on your domain needs
- **Monitor costs**: Check `web_searches` in statistics

## 🐛 Troubleshooting

### "Missing required environment variables"

**Solution**: Copy `.env.example` to `.env` and add your OpenAI API key.

### "API key appears to be a placeholder"

**Solution**: Replace `your_openai_api_key_here` with your actual key in `.env`.

### No web search results

**Solution**: 
- Verify your OpenAI API key has access to web search
- Check that you haven't hit the search limit (max 3 per query)
- Ensure you have internet connectivity

### Library not persisting

**Solution**: 
- Check write permissions on `LIBRARY_DB_PATH` directory
- Ensure sufficient disk space
- Verify ChromaDB installation: `pip install chromadb`

### "Maximum iteration limit reached"

**Solution**:
- Your question might be too complex or ambiguous
- Try breaking it into smaller, more specific questions
- Check if the agent is getting stuck in a tool-calling loop

## 📊 Performance Tips

1. **Build Your Library**: Answer common questions once, reuse forever
2. **Use Tags Wisely**: Consistent topic tags improve retrieval
3. **Monitor Staleness**: Run `--stats` to see stale entry count
4. **Batch Questions**: Use single-query mode for scripting

## 🤝 Contributing

When adding features:

1. Follow security guidelines (no secrets in code)
2. Add tests to `tests.py`
3. Update this README
4. Maintain the library-first principle

## 📄 License

MIT License - See LICENSE file for details.

## 🙋 Support

For issues or questions:
1. Check troubleshooting section above
2. Review test output: `python tests.py`
3. Verify API key configuration
4. Check OpenAI API status

## 🔄 Changelog

### v1.0 (2026-02-06)
- Initial release
- Library-first research workflow
- OpenAI integration with web search
- Vector-based storage with ChromaDB
- Configurable TTL by topic
- Comprehensive test suite
- Security-first design

---

# Artifact Critic (Gemini 3 Multimodal Feedback)

An AI-powered artifact reviewer that provides structured, actionable feedback on PDFs, images, videos, audio, slide decks, and diagrams using Google's Gemini multimodal capabilities.

## 🎯 Key Features

- **Multimodal Review**: Analyzes PDFs, PowerPoint, images, videos, and audio with visual and content understanding
- **Structured Rubrics**: Version-controlled YAML rubrics for consistent evaluation
- **Actionable Feedback**: Evidence + Location + Recommendation + Suggested rewrites
- **Repair Loop**: Iterative improvement until quality threshold met
- **Severity Levels**: Blocker → High → Medium → Low prioritization
- **JSON Output**: Machine-readable results for agent automation
- **Security Checks**: Detects accidentally exposed secrets in artifacts

## 📦 What Can It Review?

- **Resumes**: Impact bullets, quantification, ATS compatibility
- **Slide Decks**: Visual hierarchy, messaging clarity, flow
- **UI Mockups**: Accessibility, consistency, information architecture
- **API Docs**: Completeness, code examples, error handling
- **Images**: Technical quality, composition, accessibility descriptions
- **Videos**: Content analysis, quality assessment, accessibility
- **Audio**: Content transcription and analysis

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install google-generativeai PyPDF2 pdf2image python-pptx Pillow PyYAML
```

### 2. Add Gemini API Key

Edit your `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your key at: https://aistudio.google.com/apikey

### 3. Basic Usage

```bash
# Review a resume
python artifact_critic.py review resume.pdf --rubric resume_v1 \
  --goal "Software engineer at FAANG" \
  --audience "Technical recruiters"

# Review with repair loop
python artifact_critic.py repair-loop slide_deck.pptx --rubric deck_v1 \
  --max-iterations 3 --score-threshold 85

# List available rubrics
python artifact_critic.py list-rubrics
```

## 📐 Architecture

```
artifact_critic.py          # Main CLI entry point
├── gemini_critic.py        # Gemini 3 review engine
├── artifact_processor.py   # PDF/PPTX/image preprocessing
├── rubric_manager.py       # Load and validate rubrics
└── rubrics/
    ├── resume_v1.yaml      # Resume evaluation criteria
    ├── deck_v1.yaml        # Presentation review rubric
    ├── ui_v1.yaml          # UI mockup standards
    └── api_docs_v1.yaml    # API documentation checklist
```

## 📋 Available Rubrics

### `resume_v1` - Resume Review
**Categories:**
- Impact & Achievement Bullets (30%)
- Clarity & Readability (25%)
- Technical Content (20%)
- ATS Compatibility (15%)
- Design & Formatting (10%)

**Best For:** Technical resumes for software engineering roles

### `deck_v1` - Presentation Deck Review  
**Categories:**
- Message & Story (30%)
- Visual Design (25%)
- Flow & Structure (20%)
- Text & Readability (15%)
- Polish & Professionalism (10%)

**Best For:** Pitch decks, technical presentations, business proposals

### `ui_v1` - UI Mockup Review
**Categories:**
- Visual Hierarchy (25%)
- Information Architecture (25%)
- Accessibility (20%)
- Consistency (15%)
- Usability (15%)

**Best For:** Web/mobile mockups, wireframes, design prototypes

### `api_docs_v1` - API Documentation Review
**Categories:**
- Completeness (30%)
- Code Examples (25%)
- Clarity & Organization (20%)
- Error Handling (15%)
- Developer Experience (10%)

**Best For:** REST API docs, SDK references, integration guides

## 🔧 Programmatic Usage

```python
from artifact_critic import ArtifactCriticTool

tool = ArtifactCriticTool()

# Single review
result = tool.review_artifact(
    file_path="resume.pdf",
    rubric_id="resume_v1",
    task_goal="Senior engineer role at startup",
    audience="Technical founders",
    constraints="Keep to one page"
)

print(f"Score: {result.overall_score}/100")
print(f"Must fix: {len(result.must_fix)} issues")

for finding in result.findings:
    if finding.severity == "blocker":
        print(f"🚫 {finding.evidence}")
        print(f"   Fix: {finding.recommendation}")

# Repair loop
final_result = tool.review_with_repair_loop(
    file_path="deck.pptx",
    rubric_id="deck_v1",
    max_iterations=3,
    score_threshold=85
)
```

## 📤 Output Format

The tool outputs JSON with this structure:

```json
{
  "overall_score": 75,
  "summary": [
    "Strong technical content but weak impact statements",
    "Good design but poor ATS compatibility"
  ],
  "findings": [
    {
      "id": "resume_001",
      "severity": "high",
      "category": "Impact & Achievement Bullets",
      "location": {"page": 1, "section": "Experience"},
      "evidence": "Bullet states 'Worked on projects' without specifics",
      "recommendation": "Quantify impact with metrics",
      "suggested_rewrite": "Led migration of 3 microservices (50K+ req/day) reducing latency by 40%"
    }
  ],
  "must_fix": ["resume_001", "resume_003"],
  "nice_to_have": ["resume_007"],
  "next_actions": [
    "Add metrics to all achievement bullets",
    "Remove subjective claims without evidence"
  ]
}
```

## 🎨 Creating Custom Rubrics

1. Create `rubrics/my_rubric_v1.yaml`:

```yaml
rubric_id: "my_rubric_v1"
version: "1.0"
description: "Reviews for technical blog posts"

categories:
  - name: "Technical Accuracy"
    weight: 40
    criteria:
      - "Code examples are correct and tested"
      - "Technical concepts explained accurately"
  
  - name: "Clarity"
    weight: 35
    criteria:
      - "Jargon is defined for target audience"
      - "Logical flow from intro to conclusion"
  
  - name: "Engagement"
    weight: 25
    criteria:
      - "Opening hook captures attention"
      - "Practical takeaways provided"

severity_mapping:
  blocker: "Factually incorrect or misleading"
  high: "Significantly harms clarity or credibility"
  medium: "Noticeable quality issue"
  low: "Minor polish opportunity"

common_findings:
  - id: "code_not_tested"
    severity: "high"
    category: "Technical Accuracy"
    evidence_pattern: "Code example in {{location}}"
    recommendation: "Test and verify code runs as shown"
```

2. Use it:
```bash
python artifact_critic.py review post.pdf --rubric my_rubric_v1
```

## 🔁 Repair Loop Workflow

The repair loop enables automated quality improvement:

```
┌─────────────────────────────────────────────┐
│ 1. Initial Review                           │
│    • Run artifact through rubric            │
│    • Get score + structured findings        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ 2. Agent Applies Fixes                      │
│    • Parse findings (evidence, location)    │
│    • Use suggested_rewrite when available   │
│    • Update artifact                        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ 3. Re-Review Updated Artifact               │
│    • Compare score to threshold             │
│    • Check if must_fix issues resolved      │
└────────────────┬────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
   [Score ≥ 85]         [Score < 85]
   [Iterations ≥ 3]     [Has must-fix]
      │                     │
      ▼                     │
    DONE ◄─────────────────┘
                 (Loop back to step 2)
```

**Exit Conditions:**
- ✅ Score meets threshold (e.g., ≥ 85/100)
- ✅ Max iterations reached (e.g., 3 rounds)
- ✅ No more must-fix issues

## ⚙️ Configuration

In `config.py`:

```python
# Artifact processing
ARTIFACT_TEMP_DIR = "./temp_artifacts"
MAX_PAGES_PER_REVIEW = 50          # Limit for large documents
PDF_TO_IMAGE_DPI = 150             # Quality vs. cost tradeoff

# Repair loop
MAX_REPAIR_ITERATIONS = 3          # Max improvement cycles
REPAIR_SCORE_THRESHOLD = 85        # Target quality score
```

## 🧪 Testing

Run acceptance tests:

```bash
python test_artifact_critic.py
```

Tests cover:
- ✅ Rubric loading and validation
- ✅ Artifact preprocessing (PDF/PPTX/image)
- ✅ JSON output contract
- ✅ Security checks (no exposed secrets)
- ✅ Review result structure

## 📚 Examples

See `examples/demo_artifact_critic.py` for detailed usage examples:

```bash
python examples/demo_artifact_critic.py
```

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists with `GEMINI_API_KEY=your_key`
- Run `Config().validate()` to check configuration

### "Failed to process PDF"
- Install poppler: 
  - Windows: Download from https://github.com/oschwartz10612/poppler-windows
  - macOS: `brew install poppler`
  - Linux: `apt-get install poppler-utils`

### "No rubric found"
- List available: `python artifact_critic.py list-rubrics`
- Check rubric ID spelling matches YAML filename

### "Score stuck at low value"
- Review must-fix findings - these are critical blockers
- Check if artifact type matches rubric (e.g., don't use `resume_v1` for slides)
- Consider if quality threshold is too high for artifact's current state

## 🔮 Advanced Usage

### Integrating with Builder Agents

```python
# Agent workflow
while not task_complete:
    # 1. Agent builds artifact
    artifact = agent.create_artifact(task)
    
    # 2. Critic reviews
    review = critic.review_artifact(artifact, rubric="ui_v1")
    
    # 3. Agent applies fixes
    if review.must_fix:
        for finding_id in review.must_fix:
            finding = next(f for f in review.findings if f.id == finding_id)
            agent.apply_fix(
                location=finding.location,
                issue=finding.evidence,
                fix=finding.suggested_rewrite
            )
    
    # 4. Check quality
    if review.overall_score >= 85:
        break
```

### Batch Processing

```python
import glob

for file_path in glob.glob("resumes/*.pdf"):
    result = tool.review_artifact(
        file_path=file_path,
        rubric_id="resume_v1",
        output_file=f"{file_path}.review.json"
    )
    
    if result.overall_score < 70:
        print(f"❌ {file_path}: Score {result.overall_score}")
    else:
        print(f"✅ {file_path}: Score {result.overall_score}")
```

---

**Remember**: This agent is a critic, not a creator. Use it to refine and polish, not to generate from scratch! 🎨✨

## Media Analysis with Artifact Critic

The Artifact Critic includes a dedicated media analyzer for images, videos, and audio files. Use `scripts/media_analyzer.py` to generate comprehensive AI-powered analyses.

### 🎯 Media Analysis Features

- **Multimodal Analysis**: Analyzes images, videos, and audio using Gemini
- **Separate Storage**: Media analyses stored independently in `media_data/`
- **Batch Processing**: Analyze entire directories at once
- **Structured Analysis**: 6-part comprehensive analysis (description, technical quality, mood, elements, uses, accessibility)
- **File Support**: JPG, PNG, GIF, BMP, WEBP
- **CLI & Interactive**: Multiple input modes for flexibility

### 📊 Usage Examples

**Single Image:**
```bash
python scripts/media_analyzer.py --file path/to/image.jpg
```

**Directory of Images:**
```bash
python scripts/media_analyzer.py --directory path/to/images/
```

**Multiple Files:**
```bash
python scripts/media_analyzer.py --file img1.jpg --file img2.png --file img3.webp
```

**Interactive Mode:**
```bash
python scripts/media_analyzer.py
```

**View All Analyses:**
```bash
python view_media.py
```

### 📦 Storage Organization

Media analyses are stored separately from the library:

```
library_data/           # Research & knowledge entries
  └── entries.json      # Library Research Agent content

media_data/             # Image/video/audio analyses  
  └── analyses.json     # Media analysis results
```

This separation keeps your research library focused on knowledge while media analyses are organized independently.

### 📐 Architecture

```
scripts/media_analyzer.py   # Main CLI for media analysis
src/media_store.py          # Storage management for analyses
media_data/                 # Separate storage directory
  └── analyses.json         # Media analyses (not in library)
view_media.py               # Utility to browse analyses
```

---

**Pro Tip**: Use `view_media.py` regularly to review and reference past analyses! 🖼️✨
