# Project Structure

This document describes the organized folder structure of the AI Toolkit project.

## 📁 Directory Layout

```
project/
├── 📄 README.md                     # Main project documentation
├── 📄 LICENSE                       # Project license
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment variables template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 config.py                     # Shared configuration (API keys, settings)
│
├── 🎯 main.py                       # Library Research Agent CLI entry point
├── 🎯 artifact_critic_cli.py        # Artifact Critic CLI entry point
│
├── 📦 src/                          # Source code (organized by module)
│   ├── library_agent/               # Library Research Agent package
│   │   ├── __init__.py              # Package exports
│   │   ├── library_store.py         # Vector storage & library management
│   │   ├── research_agent.py        # Main agent with OpenAI integration
│   │   └── agent_tools.py           # Tool definitions for function calling
│   │
│   └── artifact_critic/             # Artifact Critic package
│       ├── __init__.py              # Package exports
│       ├── artifact_critic.py       # Main CLI tool & orchestration
│       ├── artifact_processor.py    # PDF/PPTX/image preprocessing
│       ├── gemini_critic.py         # Gemini 3 review engine
│       └── rubric_manager.py        # YAML rubric loading
│
├── 🧪 tests/                        # Test suite
│   ├── __init__.py
│   ├── test_library_agent.py        # Library Research Agent tests (23 tests)
│   └── test_artifact_critic.py      # Artifact Critic tests (24 tests)
│
├── 📚 docs/                         # Documentation
│   ├── QUICKSTART.md                # Quick start guide
│   ├── ARTIFACT_CRITIC_COMPLETE.md  # Artifact Critic implementation details
│   └── android_research_summary.md  # Research demo results
│
├── 🔧 scripts/                      # Utility scripts
│   ├── populate_android_knowledge.py       # Seed library with Android knowledge
│   └── update_library_with_critic.py       # Add Artifact Critic info to library
│
├── 📖 examples/                     # Example code and artifacts
│   ├── examples.py                  # Library Research Agent examples
│   ├── demo_artifact_critic.py      # Artifact Critic demonstrations
│   └── artifacts/                   # Sample artifacts for testing
│       └── sample_resume.txt        # Example resume
│
├── ⚙️ rubrics/                      # Evaluation rubrics (YAML)
│   ├── resume_v1.yaml               # Resume review criteria
│   ├── deck_v1.yaml                 # Presentation deck criteria
│   ├── ui_v1.yaml                   # UI mockup criteria
│   └── api_docs_v1.yaml             # API documentation criteria
│
├── 💾 library_data/                 # Library storage (runtime data)
│   └── entries.json                 # Library entries (JSON fallback)
│
└── 🗂️ temp_artifacts/               # Temporary files for artifact processing
```

## 🎯 Entry Points

### Library Research Agent
```bash
python main.py                        # Interactive mode
python main.py -q "your question"     # Single query
python main.py --stats                # Library statistics
```

### Artifact Critic
```bash
python artifact_critic_cli.py --list-rubrics                    # List rubrics
python artifact_critic_cli.py review file.pdf --rubric resume_v1  # Review artifact
python artifact_critic_cli.py --help                            # Show help
```

## 📦 Package Structure

### `src/library_agent/`
**Purpose**: Library-first research agent with curated knowledge

**Key Components**:
- `library_store.py` - ChromaDB/JSON storage backend
- `research_agent.py` - OpenAI agent with tool calling
- `agent_tools.py` - Library search, add, stats functions

**Imports**:
```python
from library_agent import LibraryStore, LibraryResearchAgent
from library_agent.library_store import LibraryEntry
```

### `src/artifact_critic/`
**Purpose**: Multimodal artifact review with Gemini 3

**Key Components**:
- `artifact_critic.py` - Main CLI tool & repair loop
- `gemini_critic.py` - Gemini API integration
- `artifact_processor.py` - File preprocessing
- `rubric_manager.py` - YAML rubric management

**Imports**:
```python
from artifact_critic import ArtifactCriticTool, GeminiCritic
from artifact_critic.rubric_manager import RubricManager
```

## 🧪 Running Tests

```bash
# Library Research Agent tests
python tests/test_library_agent.py

# Artifact Critic tests
python tests/test_artifact_critic.py

# Or use pytest
pytest tests/
```

## 📝 Configuration

All configuration is centralized in `config.py` at the project root:

```python
# Loads from .env file
OPENAI_API_KEY          # For Library Research Agent
GEMINI_API_KEY          # For Artifact Critic
LIBRARY_DB_PATH         # Library storage location
ARTIFACT_TEMP_DIR       # Temporary processing directory
```

## 🔧 Utility Scripts

Located in `scripts/` for maintenance and setup tasks:

```bash
# Populate library with Android knowledge
python scripts/populate_android_knowledge.py

# Add Artifact Critic info to library
python scripts/update_library_with_critic.py
```

## 📖 Documentation

All documentation in `docs/`:

- **QUICKSTART.md** - Getting started guide
- **ARTIFACT_CRITIC_COMPLETE.md** - Implementation details
- **android_research_summary.md** - Demo results

## 🎨 Design Principles

### 1. **Separation of Concerns**
- Each tool has its own package
- Shared config at root level
- Tests isolated in `tests/`

### 2. **Clear Entry Points**
- `main.py` - Library Research Agent
- `artifact_critic_cli.py` - Artifact Critic
- Both in root for easy access

### 3. **Minimal Root Clutter**
- Only entry points and config in root
- Source code in `src/`
- Tests in `tests/`
- Documentation in `docs/`

### 4. **Easy Imports**
- Packages use `__init__.py` for clean exports
- Relative imports within packages
- Absolute imports for shared config

### 5. **Data Separation**
- Runtime data in `library_data/`
- Temporary files in `temp_artifacts/`
- Configuration in `rubrics/`

## 🚀 Adding New Features

### New Tool Package
1. Create directory: `src/my_tool/`
2. Add `__init__.py` with exports
3. Implement modules
4. Create entry point in root: `my_tool_cli.py`
5. Add tests: `tests/test_my_tool.py`
6. Document in `docs/my_tool.md`

### New Rubric
1. Create YAML: `rubrics/my_rubric_v1.yaml`
2. Follow existing rubric structure
3. Test with: `python artifact_critic_cli.py --list-rubrics`

### New Utility Script
1. Create: `scripts/my_script.py`
2. Add imports for src packages
3. Document usage in this file

## 📊 File Count Summary

- **Source files**: 13 Python modules
- **Tests**: 2 test suites (47 total tests)
- **Rubrics**: 4 YAML files
- **Documentation**: 4 Markdown files
- **Scripts**: 2 utility scripts
- **Examples**: 2 demo files

## ✅ Migration Checklist

When moving files to new locations, ensure:

- [x] Update all import statements
- [x] Create `__init__.py` for packages
- [x] Update sys.path in entry points
- [x] Test all CLI commands
- [x] Run full test suite
- [x] Verify examples work
- [x] Update documentation references

---

**Last Updated**: February 6, 2026  
**Structure Version**: 2.0 (Organized)
