"""
Library Research Agent - Main agent implementation.
Uses OpenAI Responses API with web search and library tools.
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from openai import OpenAI

# Add parent directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config, sanitize_for_logging
from .library_store import LibraryStore, LibraryEntry
from .agent_tools import AgentTools, TOOL_SCHEMAS, extract_citations_from_response


AGENT_SYSTEM_PROMPT = """You are the Library Research Agent - an expert research assistant with access to a curated knowledge library.

**ROLE & SECURITY:**
- You help users find accurate, well-sourced information
- NEVER request, reveal, print, log, or mention API keys, tokens, passwords, or .env file contents
- If you detect potential secrets in messages, warn the user to rotate their keys immediately
- You operate with keys in the environment; you should never "see" them

**RESEARCH WORKFLOW:**
1. **Library-First Approach:** Always search the internal library FIRST using search_library()
2. **Assess Freshness:** Check if library entries are stale (is_stale: true) or missing
3. **Information Sources:** Currently working with library knowledge base
4. **Library Write-Back:** Store valuable information using add_to_library() for future use

**SOURCE QUALITY RULES:**
- Prioritize: Official documentation, standards bodies, primary sources, reputable publishers
- Cross-check: Use 2-5 independent sources for important claims when feasible
- Flag conflicts: If sources disagree, present both views
- Label credibility: Note when using lower-credibility sources (and explain why)
- Never fabricate sources or citations

**OUTPUT REQUIREMENTS:**
Every response must include:
1. **Clear Answer:** Direct, actionable response to the user's question
2. **Library Status:** Note if information is from library or if more research is needed
3. **Sources/Citations:** Links and citations for all factual claims

**BEHAVIOR:**
- Search library thoroughly before indicating information is missing
- Acknowledge uncertainty rather than guessing
- Credit library entries when used

Remember: You maintain a high-quality knowledge library. Be thorough in searching existing knowledge before indicating information is unavailable.
"""


class LibraryResearchAgent:
    """Main research agent with OpenAI integration."""
    
    def __init__(self, library_store: LibraryStore):
        """Initialize the research agent."""
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.library = library_store
        self.tools = AgentTools(library_store)
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Track for reporting
        self.last_query_stats = {
            "library_searches": 0,
            "web_searches": 0,
            "library_updates": 0,
            "sources_used": []
        }
    
    def answer_question(self, question: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Answer a user question using library-first approach with web search fallback.
        
        Args:
            question: User's question
            max_iterations: Maximum tool-calling iterations to prevent infinite loops
            
        Returns:
            Dict with 'answer', 'library_updates', 'sources', and 'stats'
        """
        # Reset counters
        self.tools.reset_search_count()
        self.last_query_stats = {
            "library_searches": 0,
            "web_searches": 0,
            "library_updates": 0,
            "sources_used": []
        }
        
        # Initialize conversation with system prompt and user question
        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]
        
        # Available tools (library tools only for now)
        # Note: Web search would require custom implementation or external API
        tools = TOOL_SCHEMAS
        
        iteration = 0
        library_updates = []
        used_library_entries = []
        
        try:
            while iteration < max_iterations:
                iteration += 1
                
                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=messages,
                    tools=tools,
                )
                
                message = response.choices[0].message
                
                # If no tool calls, we have the final answer
                if not message.tool_calls:
                    final_answer = message.content or "No answer provided."
                    
                    # Extract citations
                    citations = extract_citations_from_response(final_answer, used_library_entries)
                    
                    return {
                        "answer": final_answer,
                        "library_updates": library_updates,
                        "sources": citations,
                        "stats": self.last_query_stats,
                    }
                
                # Process tool calls
                messages.append(message)
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    
                    # Parse arguments
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # Execute tool
                    if tool_name == "search_library":
                        self.last_query_stats["library_searches"] += 1
                        result = self.tools.execute_tool(tool_name, arguments)
                        
                        # Track library entries used
                        try:
                            result_data = json.loads(result)
                            if "results" in result_data:
                                for r in result_data["results"]:
                                    entry = LibraryEntry(
                                        title=r["title"],
                                        url=r["url"],
                                        publisher=r["publisher"],
                                        topic_tags=r["topic_tags"],
                                        summary=r["summary"],
                                        key_facts=r["key_facts"],
                                        credibility_notes=r["credibility_notes"],
                                    )
                                    used_library_entries.append(entry)
                                    self.last_query_stats["sources_used"].append(r["url"])
                        except:
                            pass
                    
                    elif tool_name == "add_to_library":
                        result = self.tools.execute_tool(tool_name, arguments)
                        
                        # Track library update
                        try:
                            result_data = json.loads(result)
                            if result_data.get("success"):
                                self.last_query_stats["library_updates"] += 1
                                library_updates.append({
                                    "action": result_data.get("action"),
                                    "title": arguments.get("title"),
                                    "url": arguments.get("url"),
                                })
                        except:
                            pass
                    
                    else:
                        result = self.tools.execute_tool(tool_name, arguments)
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            
            # Max iterations reached
            return {
                "answer": "Maximum iteration limit reached. Please try rephrasing your question.",
                "library_updates": library_updates,
                "sources": [],
                "stats": self.last_query_stats,
            }
            
        except Exception as e:
            error_msg = str(e)
            # Sanitize error message
            safe_error = sanitize_for_logging(error_msg)
            
            return {
                "answer": f"An error occurred: {safe_error}",
                "library_updates": library_updates,
                "sources": [],
                "stats": self.last_query_stats,
            }
    
    def get_library_status(self) -> Dict[str, Any]:
        """Get current library statistics."""
        return self.library.get_stats()


def format_response(result: Dict[str, Any]) -> str:
    """Format agent response for display."""
    output = []
    
    # Answer section
    output.append("=" * 80)
    output.append("ANSWER")
    output.append("=" * 80)
    output.append(result["answer"])
    output.append("")
    
    # Library updates section
    if result["library_updates"]:
        output.append("=" * 80)
        output.append("LIBRARY UPDATES")
        output.append("=" * 80)
        for update in result["library_updates"]:
            output.append(f"• {update['action'].upper()}: {update['title']}")
            output.append(f"  URL: {update['url']}")
        output.append("")
    
    # Sources section
    if result["sources"]:
        output.append("=" * 80)
        output.append("SOURCES")
        output.append("=" * 80)
        for i, source in enumerate(result["sources"], 1):
            output.append(f"{i}. {source['title']}")
            output.append(f"   URL: {source['url']}")
            output.append(f"   Publisher: {source['publisher']}")
            if source.get('date_accessed'):
                output.append(f"   Accessed: {source['date_accessed']}")
        output.append("")
    
    # Statistics
    stats = result["stats"]
    output.append("=" * 80)
    output.append("QUERY STATISTICS")
    output.append("=" * 80)
    output.append(f"Library searches: {stats['library_searches']}")
    output.append(f"Web searches: {stats['web_searches']}")
    output.append(f"Library updates: {stats['library_updates']}")
    output.append("=" * 80)
    
    return "\n".join(output)
