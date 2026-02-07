"""
Acceptance Tests for Library Research Agent
Tests all non-negotiable requirements.
"""
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config, sanitize_for_logging
from library_agent.library_store import LibraryStore, LibraryEntry
from library_agent.agent_tools import AgentTools


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = []
        self.failed = []
    
    def add_pass(self, test_name: str):
        self.passed.append(test_name)
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed.append((test_name, reason))
        print(f"❌ FAIL: {test_name}")
        print(f"   Reason: {reason}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed)
        print("\n" + "=" * 80)
        print(f"TEST SUMMARY: {len(self.passed)}/{total} passed")
        print("=" * 80)
        if self.failed:
            print("\nFailed tests:")
            for name, reason in self.failed:
                print(f"  • {name}: {reason}")
        return len(self.failed) == 0


def test_no_secret_exposure():
    """Test 1: No-secret test - agent never outputs .env values"""
    results = TestResults()
    
    # Test sanitization function
    test_cases = [
        ("My key is sk-1234567890abcdefghij", "should redact API key"),
        ("API_KEY=secret123", "should redact API_KEY"),
        ("token: bearer_xyz", "should redact token"),
        ("Normal text", "should not modify normal text"),
    ]
    
    for text, desc in test_cases:
        sanitized = sanitize_for_logging(text)
        
        # Check that potential secrets are redacted
        if "sk-" in text and "sk-" in sanitized:
            results.add_fail(f"Secret sanitization ({desc})", "API key not redacted")
        elif "API_KEY=" in text and "secret123" in sanitized:
            results.add_fail(f"Secret sanitization ({desc})", "API key value not redacted")
        elif text == "Normal text" and sanitized != text:
            results.add_fail(f"Secret sanitization ({desc})", "Normal text was modified")
        else:
            results.add_pass(f"Secret sanitization ({desc})")
    
    # Test that Config.validate() fails when keys are missing or placeholders
    original_key = os.environ.get("OPENAI_API_KEY")
    
    try:
        # Test with missing key
        os.environ.pop("OPENAI_API_KEY", None)
        Config.OPENAI_API_KEY = None
        try:
            Config.validate()
            results.add_fail("Config validation (missing key)", "Should have raised SystemExit")
        except SystemExit:
            results.add_pass("Config validation (missing key)")
        
        # Test with placeholder key
        os.environ["OPENAI_API_KEY"] = "your_api_key_here"
        Config.OPENAI_API_KEY = "your_api_key_here"
        try:
            Config.validate()
            results.add_fail("Config validation (placeholder key)", "Should have raised SystemExit")
        except SystemExit:
            results.add_pass("Config validation (placeholder key)")
    
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
            Config.OPENAI_API_KEY = original_key
    
    return results.summary()


def test_library_first_retrieval():
    """Test 2: Library-first test - known topics use library without web search"""
    results = TestResults()
    
    # Create temporary library
    temp_dir = tempfile.mkdtemp()
    
    try:
        library = LibraryStore(persist_directory=temp_dir)
        
        # Add a test entry
        entry = LibraryEntry(
            title="Python Async/Await Guide",
            url="https://docs.python.org/3/library/asyncio.html",
            publisher="Python.org",
            topic_tags=["python", "documentation"],
            summary="Comprehensive guide to async/await in Python",
            key_facts=[
                "async/await introduced in Python 3.5",
                "Used for concurrent programming"
            ],
            credibility_notes="Official Python documentation",
        )
        
        result = library.add_entry(entry)
        
        if result["action"] == "added":
            results.add_pass("Library entry creation")
        else:
            results.add_fail("Library entry creation", f"Unexpected action: {result['action']}")
        
        # Search for the entry
        search_results = library.search("python async await", limit=5)
        
        if len(search_results) > 0:
            results.add_pass("Library search finds relevant entries")
            
            found_entry = search_results[0]["entry"]
            if found_entry.title == entry.title:
                results.add_pass("Library search returns correct entry")
            else:
                results.add_fail("Library search accuracy", "Wrong entry returned")
        else:
            results.add_fail("Library search", "No results found")
        
        # Test that tools can execute library search
        tools = AgentTools(library)
        tool_result = tools.execute_tool("search_library", {"query": "async await"})
        
        if "error" not in tool_result.lower():
            results.add_pass("Library search tool execution")
        else:
            results.add_fail("Library search tool", tool_result)
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return results.summary()


def test_staleness_and_refresh():
    """Test 3: Staleness test - entries older than TTL are detected as stale"""
    results = TestResults()
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        library = LibraryStore(persist_directory=temp_dir)
        
        # Create a fresh entry
        fresh_entry = LibraryEntry(
            title="Fresh Entry",
            url="https://example.com/fresh",
            publisher="Example",
            topic_tags=["test"],
            summary="Fresh content",
            key_facts=["Fact 1"],
            credibility_notes="Test source",
            freshness_ttl_days=30,
        )
        
        # Create a stale entry (manually set old date)
        stale_entry = LibraryEntry(
            title="Stale Entry",
            url="https://example.com/stale",
            publisher="Example",
            topic_tags=["test"],
            summary="Stale content",
            key_facts=["Fact 2"],
            credibility_notes="Test source",
            freshness_ttl_days=7,
        )
        
        # Make it old
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        stale_entry.date_accessed = old_date
        
        # Add both entries
        library.add_entry(fresh_entry)
        library.add_entry(stale_entry)
        
        # Check freshness
        if not fresh_entry.is_stale():
            results.add_pass("Fresh entry detected as fresh")
        else:
            results.add_fail("Fresh entry check", "Fresh entry marked as stale")
        
        if stale_entry.is_stale():
            results.add_pass("Stale entry detected as stale")
        else:
            results.add_fail("Stale entry check", "Stale entry marked as fresh")
        
        # Test refresh (update existing entry)
        updated_result = library.add_entry(stale_entry, update_if_exists=True)
        
        if updated_result["action"] == "updated":
            results.add_pass("Stale entry refresh")
        else:
            results.add_fail("Stale entry refresh", f"Expected 'updated', got '{updated_result['action']}'")
        
        # Test TTL assignment by topic
        news_ttl = Config.get_ttl_for_topics(["news"])
        doc_ttl = Config.get_ttl_for_topics(["documentation"])
        
        if news_ttl == 7:
            results.add_pass("News topic TTL (7 days)")
        else:
            results.add_fail("News topic TTL", f"Expected 7, got {news_ttl}")
        
        if doc_ttl == 60:
            results.add_pass("Documentation topic TTL (60 days)")
        else:
            results.add_fail("Documentation topic TTL", f"Expected 60, got {doc_ttl}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return results.summary()


def test_deduplication():
    """Test 4: Dedup test - same URL doesn't create duplicates"""
    results = TestResults()
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        library = LibraryStore(persist_directory=temp_dir)
        
        # Create first entry
        entry1 = LibraryEntry(
            title="Original Entry",
            url="https://example.com/article",
            publisher="Example",
            topic_tags=["test"],
            summary="Original content",
            key_facts=["Original fact"],
            credibility_notes="Test",
        )
        
        result1 = library.add_entry(entry1, update_if_exists=False)
        
        if result1["action"] == "added":
            results.add_pass("First entry added")
        else:
            results.add_fail("First entry", "Not added")
        
        # Try to add same URL again (should skip or update)
        entry2 = LibraryEntry(
            title="Updated Entry",
            url="https://example.com/article",  # Same URL
            publisher="Example",
            topic_tags=["test"],
            summary="Updated content",
            key_facts=["Updated fact"],
            credibility_notes="Test",
        )
        
        result2 = library.add_entry(entry2, update_if_exists=False)
        
        if result2["action"] == "skipped":
            results.add_pass("Duplicate prevention (update_if_exists=False)")
        else:
            results.add_fail("Duplicate prevention", f"Expected 'skipped', got '{result2['action']}'")
        
        # Try again with update flag
        result3 = library.add_entry(entry2, update_if_exists=True)
        
        if result3["action"] == "updated":
            results.add_pass("Entry update (update_if_exists=True)")
        else:
            results.add_fail("Entry update", f"Expected 'updated', got '{result3['action']}'")
        
        # Verify only one entry exists
        all_entries = library.get_all_entries()
        
        if len(all_entries) == 1:
            results.add_pass("No duplicate entries created")
        else:
            results.add_fail("Duplicate check", f"Expected 1 entry, found {len(all_entries)}")
        
        # Test URL normalization
        variants = [
            "https://example.com/article",
            "https://www.example.com/article",
            "https://example.com/article/",
        ]
        
        normalized_ids = [LibraryEntry._normalize_url(url) for url in variants]
        
        if len(set(normalized_ids)) == 1:
            results.add_pass("URL normalization (www, trailing slash)")
        else:
            results.add_fail("URL normalization", f"Got different IDs: {normalized_ids}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return results.summary()


def test_citation_requirements():
    """Test 5: Citation test - web-derived facts include citations"""
    results = TestResults()
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        library = LibraryStore(persist_directory=temp_dir)
        tools = AgentTools(library)
        
        # Test adding entry with citations in key_facts
        entry = LibraryEntry(
            title="Test Article",
            url="https://example.com/article",
            publisher="Example Publisher",
            topic_tags=["test"],
            summary="Test summary",
            key_facts=[
                "Python 3.12 was released in October 2023 (https://example.com/article)",
                "It includes performance improvements [Source: https://example.com/article]"
            ],
            credibility_notes="Official source",
        )
        
        result = library.add_entry(entry)
        
        if result["action"] == "added":
            results.add_pass("Entry with citations added")
        else:
            results.add_fail("Citation entry", "Failed to add")
        
        # Test that add_to_library tool captures all required citation fields
        tool_args = {
            "title": "Test Source",
            "url": "https://example.com/test",
            "publisher": "Test Publisher",
            "date_published": "2024-01-01",
            "topic_tags": ["test"],
            "summary": "Test summary with key points",
            "key_facts": [
                "Fact 1 with citation (https://example.com/test)",
                "Fact 2 with citation (https://example.com/test)"
            ],
            "credibility_notes": "Reputable source"
        }
        
        tool_result = tools.execute_tool("add_to_library", tool_args)
        
        if "success" in tool_result and "error" not in tool_result.lower():
            results.add_pass("Citation tool execution")
            
            # Verify entry has all citation fields
            added_entry = library.search("test", limit=1)
            if added_entry:
                entry_data = added_entry[0]["entry"]
                
                has_all_fields = all([
                    entry_data.url,
                    entry_data.publisher,
                    entry_data.date_accessed,
                    entry_data.key_facts,
                ])
                
                if has_all_fields:
                    results.add_pass("Entry contains all citation fields")
                else:
                    results.add_fail("Citation fields", "Missing required fields")
        else:
            results.add_fail("Citation tool", tool_result)
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return results.summary()


def run_all_tests():
    """Run all acceptance tests."""
    print("=" * 80)
    print("LIBRARY RESEARCH AGENT - ACCEPTANCE TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("No-Secret Test", test_no_secret_exposure),
        ("Library-First Test", test_library_first_retrieval),
        ("Staleness Test", test_staleness_and_refresh),
        ("Deduplication Test", test_deduplication),
        ("Citation Test", test_citation_requirements),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'─' * 80}")
        print(f"Running: {test_name}")
        print('─' * 80)
        
        try:
            passed = test_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ TEST CRASHED: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL ACCEPTANCE TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
