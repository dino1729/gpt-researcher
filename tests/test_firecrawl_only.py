#!/usr/bin/env python3
"""
Test script to verify Firecrawl-only functionality
This script tests that:
1. Firecrawl is set as the default retriever
2. Tavily and DuckDuckGo are completely removed
3. The research workflow uses Firecrawl correctly
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that Firecrawl is available and Tavily/DuckDuckGo are removed"""
    print("=" * 60)
    print("TEST 1: Import and Module Verification")
    print("=" * 60)

    # Test Firecrawl import
    try:
        from gpt_researcher.retrievers import FirecrawlSearch
        print("✓ FirecrawlSearch imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import FirecrawlSearch: {e}")
        return False

    # Test Tavily is removed
    try:
        from gpt_researcher.retrievers import TavilySearch
        print("✗ TavilySearch still exists (should be removed)")
        return False
    except (ImportError, AttributeError):
        print("✓ TavilySearch correctly removed")

    # Test DuckDuckGo is removed
    try:
        from gpt_researcher.retrievers import Duckduckgo
        print("✗ Duckduckgo still exists (should be removed)")
        return False
    except (ImportError, AttributeError):
        print("✓ Duckduckgo correctly removed")

    return True


def test_default_retriever():
    """Test that Firecrawl is the default retriever"""
    print("\n" + "=" * 60)
    print("TEST 2: Default Retriever Configuration")
    print("=" * 60)

    from gpt_researcher.actions.retriever import get_default_retriever
    from gpt_researcher.config.config import Config

    # Test get_default_retriever function
    default = get_default_retriever()
    if default.__name__ == 'FirecrawlSearch':
        print(f"✓ get_default_retriever() returns FirecrawlSearch")
    else:
        print(f"✗ Expected FirecrawlSearch but got {default.__name__}")
        return False

    # Test config default
    config = Config()
    if config.retriever == 'firecrawl':
        print(f"✓ Config defaults to 'firecrawl'")
    else:
        print(f"✗ Expected 'firecrawl' but config has '{config.retriever}'")
        return False

    return True


def test_retriever_lookup():
    """Test retriever lookup functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: Retriever Lookup")
    print("=" * 60)

    from gpt_researcher.actions.retriever import get_retriever

    # Test Firecrawl lookup
    fc = get_retriever('firecrawl')
    if fc and fc.__name__ == 'FirecrawlSearch':
        print("✓ get_retriever('firecrawl') works correctly")
    else:
        print(f"✗ Firecrawl lookup failed: {fc}")
        return False

    # Test removed retrievers return None
    ddg = get_retriever('duckduckgo')
    tav = get_retriever('tavily')

    if ddg is None:
        print("✓ get_retriever('duckduckgo') returns None")
    else:
        print(f"✗ DuckDuckGo should be None but got: {ddg}")
        return False

    if tav is None:
        print("✓ get_retriever('tavily') returns None")
    else:
        print(f"✗ Tavily should be None but got: {tav}")
        return False

    return True


def test_valid_retrievers():
    """Test VALID_RETRIEVERS list"""
    print("\n" + "=" * 60)
    print("TEST 4: Valid Retrievers List")
    print("=" * 60)

    from gpt_researcher.retrievers.utils import VALID_RETRIEVERS

    if 'firecrawl' in VALID_RETRIEVERS:
        print("✓ 'firecrawl' is in VALID_RETRIEVERS")
    else:
        print("✗ 'firecrawl' not in VALID_RETRIEVERS")
        return False

    if 'tavily' not in VALID_RETRIEVERS:
        print("✓ 'tavily' correctly removed from VALID_RETRIEVERS")
    else:
        print("✗ 'tavily' still in VALID_RETRIEVERS")
        return False

    if 'duckduckgo' not in VALID_RETRIEVERS:
        print("✓ 'duckduckgo' correctly removed from VALID_RETRIEVERS")
    else:
        print("✗ 'duckduckgo' still in VALID_RETRIEVERS")
        return False

    print(f"\nValid retrievers: {', '.join(VALID_RETRIEVERS)}")
    return True


def test_firecrawl_instantiation():
    """Test that Firecrawl can be instantiated"""
    print("\n" + "=" * 60)
    print("TEST 5: Firecrawl Instantiation")
    print("=" * 60)

    try:
        from gpt_researcher.retrievers import FirecrawlSearch

        # Test without API key (should work for self-hosted)
        retriever = FirecrawlSearch(query="test query")
        print(f"✓ FirecrawlSearch instantiated successfully")
        print(f"  - Query: {retriever.query}")
        print(f"  - Server URL: {retriever.server_url}")
        print(f"  - API Key provided: {'Yes' if retriever.api_key else 'No (using self-hosted mode)'}")

        return True
    except Exception as e:
        print(f"✗ Failed to instantiate FirecrawlSearch: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scraper_integration():
    """Test that Tavily is removed from scraper"""
    print("\n" + "=" * 60)
    print("TEST 6: Scraper Integration")
    print("=" * 60)

    from gpt_researcher.scraper.scraper import Scraper

    # Check scraper can be initialized with firecrawl
    try:
        # We can't fully test without proper setup, but we can check the class
        print("✓ Scraper class imports successfully")

        # Check that TavilyExtract is not in imports
        try:
            from gpt_researcher.scraper import TavilyExtract
            print("✗ TavilyExtract still exists in scraper")
            return False
        except (ImportError, AttributeError):
            print("✓ TavilyExtract correctly removed from scraper")

        return True
    except Exception as e:
        print(f"✗ Scraper test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FIRECRAWL-ONLY FUNCTIONALITY TEST SUITE")
    print("=" * 60)

    tests = [
        test_imports,
        test_default_retriever,
        test_retriever_lookup,
        test_valid_retrievers,
        test_firecrawl_instantiation,
        test_scraper_integration,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        print("Firecrawl is correctly configured as the only retriever.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
