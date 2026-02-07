"""
Tool definitions and implementations for the Library Research Agent.
Handles library queries, web search, and library updates.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config
from .library_store import LibraryStore, LibraryEntry


# Tool schemas for OpenAI function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_library",
            "description": "Search the internal knowledge library for relevant information. Use this FIRST before web search. Returns entries with freshness status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant library entries"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_library",
            "description": "Add or update an entry in the knowledge library. Use this after finding valuable information from web search to store it for future use.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Clear, descriptive title for the entry"
                    },
                    "url": {
                        "type": "string",
                        "description": "Source URL"
                    },
                    "publisher": {
                        "type": "string",
                        "description": "Publisher or website name"
                    },
                    "date_published": {
                        "type": "string",
                        "description": "Publication date if available (ISO format or descriptive)"
                    },
                    "topic_tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of topic tags (e.g., ['technology', 'documentation'])"
                    },
                    "summary": {
                        "type": "string",
                        "description": "5-10 bullet point summary of key information"
                    },
                    "key_facts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of key facts with inline citations to the URL"
                    },
                    "credibility_notes": {
                        "type": "string",
                        "description": "Why this source is trustworthy (official docs, expert author, etc.)"
                    }
                },
                "required": ["title", "url", "publisher", "topic_tags", "summary", "key_facts", "credibility_notes"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_library_stats",
            "description": "Get statistics about the knowledge library (total entries, freshness, topics)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


class AgentTools:
    """Tool implementations for the research agent."""
    
    def __init__(self, library_store: LibraryStore):
        self.library = library_store
        self.web_search_count = 0
        self.max_searches = Config.MAX_WEB_SEARCHES_PER_QUERY
    
    def reset_search_count(self):
        """Reset web search counter for a new query."""
        self.web_search_count = 0
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool and return results as JSON string.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments as dict
            
        Returns:
            JSON string with results
        """
        try:
            if tool_name == "search_library":
                return self._search_library(arguments)
            elif tool_name == "add_to_library":
                return self._add_to_library(arguments)
            elif tool_name == "get_library_stats":
                return self._get_library_stats(arguments)
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except Exception as e:
            return json.dumps({"error": f"Tool execution failed: {str(e)}"})
    
    def _search_library(self, args: Dict[str, Any]) -> str:
        """Search the library for relevant entries."""
        query = args.get("query", "")
        limit = args.get("limit", 5)
        
        if not query:
            return json.dumps({"error": "Query is required"})
        
        results = self.library.search(query, limit=limit, filter_stale=False)
        
        # Format results
        formatted_results = []
        for r in results:
            entry = r["entry"]
            formatted_results.append({
                "title": entry.title,
                "url": entry.url,
                "publisher": entry.publisher,
                "date_published": entry.date_published,
                "date_accessed": entry.date_accessed,
                "topic_tags": entry.topic_tags,
                "summary": entry.summary,
                "key_facts": entry.key_facts,
                "credibility_notes": entry.credibility_notes,
                "relevance_score": round(r["score"], 3),
                "is_stale": r["is_stale"],
                "freshness_ttl_days": entry.freshness_ttl_days,
            })
        
        return json.dumps({
            "found": len(formatted_results),
            "results": formatted_results,
            "message": f"Found {len(formatted_results)} relevant entries in library"
        }, indent=2)
    
    def _add_to_library(self, args: Dict[str, Any]) -> str:
        """Add or update a library entry."""
        try:
            # Determine TTL based on topics
            topic_tags = args.get("topic_tags", [])
            ttl_days = Config.get_ttl_for_topics(topic_tags)
            
            # Create entry
            entry = LibraryEntry(
                title=args["title"],
                url=args["url"],
                publisher=args["publisher"],
                date_published=args.get("date_published"),
                topic_tags=topic_tags,
                summary=args["summary"],
                key_facts=args["key_facts"],
                credibility_notes=args["credibility_notes"],
                freshness_ttl_days=ttl_days,
            )
            
            # Add to library (will update if exists)
            result = self.library.add_entry(entry, update_if_exists=True)
            
            return json.dumps({
                "success": True,
                "action": result["action"],
                "entry_id": result["entry_id"],
                "reason": result["reason"],
                "ttl_days": ttl_days,
                "message": f"Entry {result['action']}: {entry.title}"
            }, indent=2)
            
        except KeyError as e:
            return json.dumps({"error": f"Missing required field: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Failed to add entry: {str(e)}"})
    
    def _get_library_stats(self, args: Dict[str, Any]) -> str:
        """Get library statistics."""
        stats = self.library.get_stats()
        return json.dumps({
            "success": True,
            "stats": stats,
            "message": f"Library contains {stats['total_entries']} entries ({stats['fresh_entries']} fresh, {stats['stale_entries']} stale)"
        }, indent=2)


def format_citation(url: str, title: str, publisher: str) -> str:
    """Format a citation for display."""
    return f"[{title}]({url}) - {publisher}"


def extract_citations_from_response(response_text: str, library_entries: List[LibraryEntry]) -> List[Dict[str, str]]:
    """Extract unique citations from response and library entries used."""
    citations = []
    seen_urls = set()
    
    for entry in library_entries:
        if entry.url not in seen_urls:
            citations.append({
                "url": entry.url,
                "title": entry.title,
                "publisher": entry.publisher,
                "date_accessed": entry.date_accessed
            })
            seen_urls.add(entry.url)
    
    return citations
