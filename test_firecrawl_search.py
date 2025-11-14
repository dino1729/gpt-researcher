#!/usr/bin/env python3
"""
Test script for Firecrawl Search Retriever
Tests the implementation with a self-hosted Firecrawl server
"""
import os
import sys

# Set environment variables for testing
os.environ["FIRECRAWL_SERVER_URL"] = "http://10.0.0.107:3002/v2"
os.environ["FIRECRAWL_API_KEY"] = ""  # Empty for passwordless server

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_researcher.retrievers.firecrawl.firecrawl_search import FirecrawlSearch


def test_firecrawl_search():
    """Test the FirecrawlSearch retriever"""
    print("=" * 60)
    print("Testing Firecrawl Search Retriever")
    print("=" * 60)
    
    # Test query
    query = "Python web scraping"
    print(f"\nTest Query: {query}")
    print(f"Server URL: {os.environ.get('FIRECRAWL_SERVER_URL')}")
    print(f"API Key: {'(empty)' if not os.environ.get('FIRECRAWL_API_KEY') else '(set)'}")
    print()
    
    # Create retriever instance
    print("Creating FirecrawlSearch instance...")
    retriever = FirecrawlSearch(query)
    
    # Verify configuration
    print(f"Base URL: {retriever.base_url}")
    print(f"Headers: {retriever.request_headers}")
    print()
    
    # Perform search
    print("Performing search (max_results=3)...")
    try:
        results = retriever.search(max_results=3)
        
        if results:
            print(f"\n✓ Success! Found {len(results)} results\n")
            
            # Display results
            for i, result in enumerate(results, 1):
                print(f"Result {i}:")
                print(f"  URL: {result.get('href', 'N/A')}")
                content = result.get('body', '')
                content_preview = content[:200] + "..." if len(content) > 200 else content
                print(f"  Content Preview: {content_preview}")
                print()
        else:
            print("\n✗ No results returned")
            
    except Exception as e:
        print(f"\n✗ Error during search: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    print("Test completed successfully! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_firecrawl_search()
    sys.exit(0 if success else 1)

