"""
View Media Analyses - Browse stored media analyses.

Quick utility to view and search media analyses.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from media_store import MediaStore


def main():
    """Main function."""
    store = MediaStore("./media_data")
    
    # Get statistics
    stats = store.get_statistics()
    
    print("\n" + "=" * 80)
    print("MEDIA ANALYSES STORAGE")
    print("=" * 80)
    print(f"\nTotal analyses: {stats['total_analyses']}")
    
    if stats['by_type']:
        print("\nBy type:")
        for media_type, count in stats['by_type'].items():
            print(f"  • {media_type}: {count}")
    
    if stats['recent_analyses']:
        print("\n" + "-" * 80)
        print("RECENT ANALYSES")
        print("-" * 80)
        
        for analysis_info in stats['recent_analyses']:
            print(f"\n📁 {analysis_info['filename']}")
            print(f"   Type: {analysis_info['media_type']}")
            print(f"   Date: {analysis_info['date']}")
    
    # Show all analyses with details
    all_analyses = store.get_all_analyses()
    
    if all_analyses:
        print("\n" + "-" * 80)
        print("ALL ANALYSES")
        print("-" * 80)
        
        for analysis in all_analyses:
            print(f"\n🖼️  {analysis.filename}")
            print(f"   Type: {analysis.media_type}")
            print(f"   Path: {analysis.filepath}")
            print(f"   Analyzed by: {analysis.analyzed_by}")
            print(f"   Date: {analysis.date_analyzed}")
            if analysis.file_size:
                print(f"   Size: {analysis.file_size:,} bytes")
            print(f"\n   Preview: {analysis.analysis_text[:200]}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
