# Firecrawl Search API Retriever

import os
from typing import Optional, List, Dict, Any
import requests
import json


class FirecrawlSearch:
    """
    Firecrawl Search API Retriever
    Uses Firecrawl's search endpoint to perform web searches and retrieve scraped content.
    """

    def __init__(self, query: str, headers: Optional[Dict] = None, query_domains: Optional[List[str]] = None):
        """
        Initializes the FirecrawlSearch object.

        Args:
            query (str): The search query string.
            headers (dict, optional): Additional headers to include in the request. Defaults to None.
            query_domains (list, optional): List of domains to include in the search. Defaults to None.
        """
        self.query = query
        self.headers = headers or {}
        self.query_domains = query_domains or None
        self.api_key = self.get_api_key()
        self.server_url = self.get_server_url()
        self.base_url = f"{self.server_url}/search"
        self.request_headers = {
            "Content-Type": "application/json",
        }
        # Add Authorization header only if API key is provided
        if self.api_key:
            self.request_headers["Authorization"] = f"Bearer {self.api_key}"

    def get_api_key(self) -> str:
        """
        Gets the Firecrawl API key from headers or environment.
        Returns empty string for passwordless self-hosted servers.
        
        Returns:
            str: API key or empty string
        """
        api_key = self.headers.get("firecrawl_api_key")
        if not api_key:
            api_key = os.environ.get("FIRECRAWL_API_KEY", "")
            if not api_key:
                print(
                    "Firecrawl API key not found (optional for self-hosted servers). "
                    "Set FIRECRAWL_API_KEY environment variable if required."
                )
        return api_key

    def get_server_url(self) -> str:
        """
        Gets the Firecrawl server URL from headers or environment.
        Defaults to official Firecrawl server if not specified.
        
        Returns:
            str: Server URL
        """
        server_url = self.headers.get("firecrawl_server_url")
        if not server_url:
            server_url = os.environ.get("FIRECRAWL_SERVER_URL", "https://api.firecrawl.dev/v1")
        
        # Remove trailing slash if present
        server_url = server_url.rstrip("/")
        
        # Ensure /v1 or /v2 is in the URL, default to v1 if not specified
        if not ("/v1" in server_url or "/v2" in server_url):
            server_url = f"{server_url}/v1"
            
        return server_url

    def search(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Performs a web search using Firecrawl's search API.
        
        Args:
            max_results (int): Maximum number of results to return. Defaults to 10.
            
        Returns:
            list: List of search results in format [{"href": url, "body": content}, ...]
        """
        try:
            print(f"Searching with Firecrawl for query: {self.query}")
            
            # Build the search request payload
            search_payload = {
                "query": self.query,
                "limit": max_results,
                "scrapeOptions": {
                    "formats": ["markdown"]
                }
            }
            
            # Add domain filtering if specified
            if self.query_domains:
                # Firecrawl doesn't have native domain filtering in search,
                # so we append site: operators to the query
                domain_query = " " + " OR ".join([f"site:{domain}" for domain in self.query_domains])
                search_payload["query"] = self.query + domain_query
            
            # Make the search request
            response = requests.post(
                self.base_url,
                headers=self.request_headers,
                data=json.dumps(search_payload),
                timeout=120
            )
            
            if response.status_code == 200:
                results = response.json()
                return self._process_results(results)
            else:
                print(f"Firecrawl search API returned status code {response.status_code}: {response.text}")
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f"Error during Firecrawl search: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error during Firecrawl search: {e}")
            return []

    def _process_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process Firecrawl search results into the expected format.
        
        Args:
            results (dict): Raw results from Firecrawl API
            
        Returns:
            list: Processed results in format [{"href": url, "body": content}, ...]
        """
        search_response = []
        
        try:
            # Check if the response contains data
            if not results.get("success", False):
                print(f"Firecrawl search was not successful: {results}")
                return search_response
            
            # Extract the data object (it's a dict with 'web', 'images', 'news' keys)
            data = results.get("data", {})
            
            if not data:
                print("No results found with Firecrawl search.")
                return search_response
            
            # Get web search results (this is an array)
            web_results = data.get("web", [])
            
            if not web_results:
                print("No web results found with Firecrawl search.")
                return search_response
            
            # Process each result
            for item in web_results:
                # Handle different response formats (with or without scraping)
                url = item.get("url") or item.get("href")
                
                # Get content - prefer markdown, fall back to description
                content = item.get("markdown", "") or item.get("description", "") or item.get("content", "")
                
                if url and content:
                    search_response.append({
                        "href": url,
                        "body": content
                    })
                elif url:
                    # If we have URL but no content, at least include the title/description
                    title = item.get("title", "")
                    description = item.get("description", "")
                    search_response.append({
                        "href": url,
                        "body": f"{title}\n\n{description}" if title else description
                    })
            
            print(f"Successfully processed {len(search_response)} results from Firecrawl")
            return search_response
            
        except Exception as e:
            print(f"Error processing Firecrawl results: {e}")
            return search_response

