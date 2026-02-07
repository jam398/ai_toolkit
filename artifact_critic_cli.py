#!/usr/bin/env python3
"""
Artifact Critic CLI - Entry point script.
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from artifact_critic.artifact_critic import main

if __name__ == "__main__":
    sys.exit(main())
