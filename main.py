"""
Library Research Agent - Main CLI Application
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config, sanitize_for_logging
from library_agent.library_store import LibraryStore
from library_agent.research_agent import LibraryResearchAgent, format_response


def print_banner():
    """Print application banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Library Research Agent v1.0                          ║
║  Curated Knowledge + Web Search with Citations              ║
╚══════════════════════════════════════════════════════════════╝
""")


def run_interactive_mode(agent: LibraryResearchAgent):
    """Run the agent in interactive mode."""
    print_banner()
    print("Interactive mode - Type your questions below.")
    print("Commands: 'stats' for library info, 'quit' to exit\n")
    
    while True:
        try:
            # Get user input
            question = input("\n🔍 Question: ").strip()
            
            if not question:
                continue
            
            # Handle commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if question.lower() == 'stats':
                stats = agent.get_library_status()
                print("\n📚 Library Statistics:")
                print(f"  Total entries: {stats['total_entries']}")
                print(f"  Fresh entries: {stats['fresh_entries']}")
                print(f"  Stale entries: {stats['stale_entries']}")
                if stats['topics']:
                    print("  Topics:", ", ".join(f"{k}({v})" for k, v in sorted(stats['topics'].items())))
                continue
            
            # Process question
            print("\n⏳ Researching...")
            result = agent.answer_question(question)
            
            # Display formatted response
            print("\n" + format_response(result))
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            safe_error = sanitize_for_logging(str(e))
            print(f"\n❌ Error: {safe_error}")


def run_single_query(agent: LibraryResearchAgent, question: str, output_file: str = None):
    """Run a single query and optionally save to file."""
    print_banner()
    print(f"Question: {question}\n")
    print("⏳ Researching...\n")
    
    result = agent.answer_question(question)
    formatted = format_response(result)
    
    # Display to console
    print(formatted)
    
    # Save to file if requested
    if output_file:
        try:
            Path(output_file).write_text(formatted, encoding='utf-8')
            print(f"\n✅ Results saved to: {output_file}")
        except Exception as e:
            print(f"\n⚠️  Failed to save to file: {e}")


def show_library_stats(agent: LibraryResearchAgent):
    """Display library statistics."""
    stats = agent.get_library_status()
    
    print_banner()
    print("📚 Library Statistics\n")
    print(f"Total entries:     {stats['total_entries']}")
    print(f"Fresh entries:     {stats['fresh_entries']}")
    print(f"Stale entries:     {stats['stale_entries']}")
    
    if stats['topics']:
        print("\nTopics:")
        for topic, count in sorted(stats['topics'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {topic}: {count} entries")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Library Research Agent - Answer questions using curated knowledge + web search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py

  # Single question
  python main.py -q "What is the latest Python version?"

  # Save results to file
  python main.py -q "Explain async/await in Python" -o results.txt

  # Show library statistics
  python main.py --stats

Security Note:
  API keys must be in .env file. Never commit .env to version control.
        """
    )
    
    parser.add_argument(
        '-q', '--question',
        type=str,
        help='Ask a single question (non-interactive mode)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file for results (used with -q)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show library statistics and exit'
    )
    
    parser.add_argument(
        '--library-path',
        type=str,
        default=Config.LIBRARY_DB_PATH,
        help=f'Path to library database (default: {Config.LIBRARY_DB_PATH})'
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
    except SystemExit:
        return 1
    
    # Initialize components
    try:
        library = LibraryStore(persist_directory=args.library_path)
        agent = LibraryResearchAgent(library)
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return 1
    
    # Run requested mode
    try:
        if args.stats:
            show_library_stats(agent)
        elif args.question:
            run_single_query(agent, args.question, args.output)
        else:
            run_interactive_mode(agent)
        
        return 0
        
    except Exception as e:
        safe_error = sanitize_for_logging(str(e))
        print(f"\n❌ Fatal error: {safe_error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
