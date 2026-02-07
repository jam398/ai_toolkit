"""
Library Research Agent - Curated knowledge with web search fallback.
"""
from .library_store import LibraryStore, LibraryEntry
from .research_agent import LibraryResearchAgent
from .agent_tools import AgentTools, TOOL_SCHEMAS, extract_citations_from_response, format_citation

__all__ = [
    'LibraryStore',
    'LibraryEntry',
    'LibraryResearchAgent',
    'AgentTools',
    'TOOL_SCHEMAS',
    'extract_citations_from_response',
    'format_citation',
]
