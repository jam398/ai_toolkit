"""
Example script demonstrating Library Research Agent usage.
This shows various use cases and integration patterns.
"""
from config import Config
from library_store import LibraryStore, LibraryEntry
from research_agent import LibraryResearchAgent


def example_basic_usage():
    """Basic usage example."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80)
    
    # Initialize
    Config.validate()
    library = LibraryStore()
    agent = LibraryResearchAgent(library)
    
    # Ask a question
    result = agent.answer_question("What is Python's asyncio library?")
    
    # Display answer
    print(result["answer"])
    print(f"\nSources used: {len(result['sources'])}")
    print(f"Web searches: {result['stats']['web_searches']}")


def example_pre_populate_library():
    """Pre-populate library with known sources."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Pre-Populating Library")
    print("=" * 80)
    
    library = LibraryStore()
    
    # Add a known high-quality source
    entry = LibraryEntry(
        title="Python asyncio Documentation",
        url="https://docs.python.org/3/library/asyncio.html",
        publisher="Python Software Foundation",
        date_published="2024-01-01",
        topic_tags=["python", "documentation", "async"],
        summary="""
• asyncio is a library for concurrent code using async/await syntax
• Provides high-level APIs for running coroutines
• Includes primitives for tasks, futures, and event loops
• Supports network I/O, subprocesses, and synchronization
• Introduced in Python 3.4, enhanced in 3.5+
        """.strip(),
        key_facts=[
            "asyncio uses async/await syntax introduced in Python 3.5",
            "Event loop is the core of asyncio execution",
            "Coroutines are declared with async def",
            "await pauses execution until awaitable completes",
        ],
        credibility_notes="Official Python documentation - authoritative source",
        freshness_ttl_days=60,
    )
    
    result = library.add_entry(entry)
    print(f"Entry {result['action']}: {entry.title}")
    print(f"Now library has {library.get_stats()['total_entries']} entries")


def example_batch_questions():
    """Process multiple questions efficiently."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Batch Questions")
    print("=" * 80)
    
    Config.validate()
    library = LibraryStore()
    agent = LibraryResearchAgent(library)
    
    questions = [
        "What is Python's GIL?",
        "What are Python type hints?",
        "What is FastAPI?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {question}")
        result = agent.answer_question(question)
        
        # Brief summary
        print(f"  → Answer length: {len(result['answer'])} chars")
        print(f"  → Library searches: {result['stats']['library_searches']}")
        print(f"  → Web searches: {result['stats']['web_searches']}")
        print(f"  → Updates: {result['stats']['library_updates']}")


def example_library_stats():
    """Display library statistics and health."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Library Statistics")
    print("=" * 80)
    
    library = LibraryStore()
    stats = library.get_stats()
    
    print(f"Total entries: {stats['total_entries']}")
    print(f"Fresh entries: {stats['fresh_entries']}")
    print(f"Stale entries: {stats['stale_entries']}")
    
    if stats['topics']:
        print("\nTopics coverage:")
        for topic, count in sorted(stats['topics'].items(), key=lambda x: x[1], reverse=True):
            freshness_pct = 100 if stats['total_entries'] == 0 else \
                (stats['fresh_entries'] / stats['total_entries']) * 100
            print(f"  • {topic}: {count} entries")
        
        print(f"\nOverall freshness: {freshness_pct:.1f}%")


def example_custom_ttl():
    """Demonstrate custom TTL configuration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Custom TTL by Topic")
    print("=" * 80)
    
    library = LibraryStore()
    
    # Add entries with different topics (and thus different TTLs)
    topics_examples = [
        (["news"], "News article about tech"),
        (["documentation"], "API documentation"),
        (["reference"], "Historical reference"),
    ]
    
    for i, (topics, title) in enumerate(topics_examples, 1):
        ttl = Config.get_ttl_for_topics(topics)
        print(f"{i}. Topics {topics} → TTL: {ttl} days")
        print(f"   Example: {title}")


def example_search_comparison():
    """Compare library vs web search performance."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Library vs Web Search")
    print("=" * 80)
    
    Config.validate()
    library = LibraryStore()
    agent = LibraryResearchAgent(library)
    
    # Question that might be in library
    question = "What is Python?"
    
    print(f"Question: {question}")
    print("\nFirst query (empty library):")
    result1 = agent.answer_question(question)
    print(f"  Web searches: {result1['stats']['web_searches']}")
    print(f"  Library updates: {result1['stats']['library_updates']}")
    
    print("\nSecond query (same question, now in library):")
    result2 = agent.answer_question(question)
    print(f"  Web searches: {result2['stats']['web_searches']}")
    print(f"  Library updates: {result2['stats']['library_updates']}")
    
    print("\n✨ Notice: Second query likely uses library instead of web!")


def main():
    """Run all examples."""
    examples = [
        example_pre_populate_library,
        example_library_stats,
        example_custom_ttl,
    ]
    
    print("\n" + "=" * 80)
    print("LIBRARY RESEARCH AGENT - USAGE EXAMPLES")
    print("=" * 80)
    print("\nThese examples demonstrate key features without making API calls.")
    print("Uncomment other examples to test with your API key.\n")
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nExample failed: {e}")
    
    print("\n" + "=" * 80)
    print("Examples complete! See README.md for more information.")
    print("=" * 80)


if __name__ == "__main__":
    main()
