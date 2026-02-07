# Quick Start Guide

This guide will get you up and running with the Library Research Agent in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- OpenAI API key with GPT-4 access

## Step-by-Step Setup

### 1. Install Dependencies

Open a terminal in the project directory:

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Your API Key

⚠️ **SECURITY WARNING**: Never commit your `.env` file or share your API keys!

The project includes `.env.example` as a template. Your actual `.env` file should contain:

```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

**If you already have a `.env` file**, verify it's in `.gitignore` and not tracked by git:

```bash
# Check if .env is gitignored
git check-ignore .env

# Should output: .env
```

### 3. Verify Installation

Run the test suite to ensure everything is working:

```bash
python tests.py
```

You should see:
```
✅ ALL ACCEPTANCE TESTS PASSED
```

### 4. Run Your First Query

**Interactive mode** (recommended for exploration):
```bash
python main.py
```

**Single question mode**:
```bash
python main.py -q "What is Python asyncio?"
```

## Example Session

```
$ python main.py

╔══════════════════════════════════════════════════════════════╗
║         Library Research Agent v1.0                          ║
║  Curated Knowledge + Web Search with Citations              ║
╚══════════════════════════════════════════════════════════════╝

Interactive mode - Type your questions below.
Commands: 'stats' for library info, 'quit' to exit

🔍 Question: What is async/await in Python?

⏳ Researching...

[Agent provides detailed answer with sources]

🔍 Question: stats

📚 Library Statistics:
  Total entries: 5
  Fresh entries: 5
  Stale entries: 0
  Topics: python(3), documentation(2), tutorial(1)

🔍 Question: quit

Goodbye!
```

## Quick Reference

### Commands in Interactive Mode

- **stats** - Show library statistics
- **quit** or **exit** - Exit the program
- Press **Ctrl+C** to interrupt at any time

### CLI Options

```bash
# Get help
python main.py --help

# Single question
python main.py -q "Your question here"

# Save output to file
python main.py -q "Your question" -o output.txt

# Show library stats
python main.py --stats

# Custom library location
python main.py --library-path /path/to/library
```

## What Happens On First Run?

1. **Library initialization**: Creates `library_data/` directory for storage
2. **OpenAI connection**: Verifies your API key
3. **First query**: Uses web search (library is empty)
4. **Knowledge building**: Stores findings for future reuse

## Tips for Best Results

1. **Ask specific questions**: "What is X?" works better than "Tell me about stuff"
2. **Let the library grow**: After a few queries, most answers come from library
3. **Check sources**: Review citations for important decisions
4. **Monitor costs**: Watch the web search count in statistics

## Common Issues

### "Missing required environment variables"

**Problem**: No API key configured

**Solution**:
```bash
# Make sure .env exists with your key
echo OPENAI_API_KEY=sk-your-key-here > .env
```

### "API key appears to be a placeholder"

**Problem**: Using example key from `.env.example`

**Solution**: Replace with your actual OpenAI API key

### Import errors

**Problem**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore configuration options in [config.py](config.py)
- Build your knowledge library by asking domain-specific questions
- Customize TTL rules for your use case

## Security Reminder

🔒 **Critical Security Rules:**

1. **NEVER** commit `.env` file to version control
2. **NEVER** share your API keys
3. **ALWAYS** use `.gitignore` to exclude sensitive files
4. **ROTATE** keys immediately if exposed

Happy researching! 📚✨
