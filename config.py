"""
Configuration management for Library Research Agent.
Security: All secrets loaded from environment only.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration with security safeguards."""
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Library storage
    LIBRARY_DB_PATH = os.getenv("LIBRARY_DB_PATH", "./library_data")
    
    # Artifact Critic settings
    ARTIFACT_TEMP_DIR = os.getenv("ARTIFACT_TEMP_DIR", "./temp_artifacts")
    MAX_PAGES_PER_REVIEW = int(os.getenv("MAX_PAGES_PER_REVIEW", "10"))
    MAX_REPAIR_ITERATIONS = int(os.getenv("MAX_REPAIR_ITERATIONS", "3"))
    REPAIR_SCORE_THRESHOLD = int(os.getenv("REPAIR_SCORE_THRESHOLD", "85"))
    
    # Agent behavior limits
    MAX_WEB_SEARCHES_PER_QUERY = int(os.getenv("MAX_WEB_SEARCHES_PER_QUERY", "3"))
    MAX_SEARCH_RESULTS_PER_SEARCH = int(os.getenv("MAX_SEARCH_RESULTS_PER_SEARCH", "5"))
    
    # Default TTL rules (days) by topic
    DEFAULT_TTL_DAYS = 30
    TOPIC_TTL_RULES = {
        "news": 7,
        "current_events": 7,
        "technology": 14,
        "research": 30,
        "documentation": 60,
        "history": 180,
        "reference": 365,
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration and check for required secrets."""
        missing = []
        
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        
        if missing:
            print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
            print("Please copy .env.example to .env and add your API keys.")
            sys.exit(1)
        
        # Security check: warn if keys look like placeholders
        if cls.OPENAI_API_KEY and "your_" in cls.OPENAI_API_KEY.lower():
            print("ERROR: OPENAI_API_KEY appears to be a placeholder.")
            print("Please add your actual API key to .env file.")
            sys.exit(1)
    
    @classmethod
    def get_ttl_for_topics(cls, topics: list[str]) -> int:
        """Get the minimum TTL for a list of topics."""
        if not topics:
            return cls.DEFAULT_TTL_DAYS
        
        ttls = [cls.TOPIC_TTL_RULES.get(topic.lower(), cls.DEFAULT_TTL_DAYS) 
                for topic in topics]
        return min(ttls)


# Security: Never log or print the actual API keys
def sanitize_for_logging(text: str) -> str:
    """Remove potential secrets from text before logging."""
    if not text:
        return text
    
    # Redact anything that looks like an API key
    import re
    patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', '[REDACTED_API_KEY]'),
        (r'API[_\s]*KEY[_\s]*[:=][_\s]*[^\s]+', 'API_KEY=[REDACTED]'),
        (r'token[_\s]*[:=][_\s]*[^\s]+', 'token=[REDACTED]'),
    ]
    
    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result
