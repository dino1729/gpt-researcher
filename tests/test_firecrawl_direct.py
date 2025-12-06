#!/usr/bin/env python3
"""
Direct test for Firecrawl Search Retriever (no dependencies)
Tests the implementation with a self-hosted Firecrawl server
"""
import os
import sys
import requests
import json

# Set environment variables for testing
SERVER_URL = "http://10.0.0.107:3002/v2"
API_KEY = ""  # Empty for passwordless server

def test_firecrawl_api():
    """Test direct API call to Firecrawl search endpoint"""
    print("=" * 60)
    print("Testing Firecrawl Search API (Direct)")
    print("=" * 60)
    
    query = "Python web scraping"
    print(f"\nTest Query: {query}")
    print(f"Server URL: {SERVER_URL}")
    print(f"API Key: {'(empty)' if not API_KEY else '(set)'}")
    print()
    
    # Build the search URL
    search_url = f"{SERVER_URL}/search"
    print(f"Search Endpoint: {search_url}")
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
    }
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    # Prepare payload
    payload = {
        "query": query,
        "limit": 3,
        "scrapeOptions": {
            "formats": ["markdown"]
        }
    }
    
    print(f"Request Payload: {json.dumps(payload, indent=2)}")
    print()
    
    # Make the request
    print("Sending request to Firecrawl server...")
    try:
        response = requests.post(
            search_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=120
        )
        
        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print(f"\n✓ Success! Response received")
            print(f"Response Keys: {list(results.keys())}")
            
            if results.get("success"):
                data = results.get("data", {})
                print(f"\nData Keys: {list(data.keys())}")
                
                web_results = data.get("web", [])
                print(f"Found {len(web_results)} web results")
                
                if web_results:
                    for i, item in enumerate(web_results, 1):
                        print(f"\nResult {i}:")
                        print(f"  URL: {item.get('url', 'N/A')}")
                        title = item.get('title', 'N/A')
                        print(f"  Title: {title}")
                        
                        markdown = item.get('markdown', '')
                        description = item.get('description', '')
                        
                        if markdown:
                            preview = markdown[:150] + "..." if len(markdown) > 150 else markdown
                            print(f"  Markdown Preview: {preview}")
                        if description:
                            print(f"  Description: {description}")
                            
                    print(f"\n✓ Successfully retrieved and processed {len(web_results)} results!")
                else:
                    print("\n⚠ No web results in response")
            else:
                print(f"\n✗ API returned success=false: {results}")
                return False
        else:
            print(f"\n✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n✗ Connection Error: Cannot connect to {SERVER_URL}")
        print(f"   Error: {e}")
        print("\n   Please verify:")
        print("   1. The Firecrawl server is running")
        print("   2. The URL is correct (http://10.0.0.107:3002/v2)")
        print("   3. The server is accessible from this machine")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("Test completed successfully! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_firecrawl_api()
    sys.exit(0 if success else 1)
