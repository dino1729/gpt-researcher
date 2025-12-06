# Firecrawl Search API Retriever

import os
import logging
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
        self.logger = logging.getLogger(__name__)
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

        # If running inside Docker and the value is localhost/127, rewrite to host.docker.internal
        if "localhost" in server_url or "127.0.0.1" in server_url:
            server_url = server_url.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
        
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
            self.logger.info(f"[Firecrawl] Searching query='%s' server='%s'", self.query, self.base_url)
            
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
            self.logger.info(
                "[Firecrawl] status=%s for %s", response.status_code, self.base_url
            )
            try:
                preview = response.text[:500]
                self.logger.debug("[Firecrawl] response preview: %s", preview)
            except Exception:
                self.logger.exception("[Firecrawl] failed to read response preview")
            
            if response.status_code == 200:
                results = response.json()
                return self._process_results(results)
            else:
                self.logger.warning(
                    "[Firecrawl] status=%s body=%s",
                    response.status_code,
                    response.text[:500],
                )
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            self.logger.error("Error during Firecrawl search: %s", e)
            return []
        except Exception as e:
            self.logger.exception("Unexpected error during Firecrawl search: %s", e)
            return []

    def _process_results(self, results: Any) -> List[Dict[str, Any]]:
        """
        Process Firecrawl search results into the expected format.
        Handles multiple response formats from official and self-hosted Firecrawl servers.

        Args:
            results: Raw results from Firecrawl API (can be dict or list)

        Returns:
            list: Processed results in format [{"href": url, "body": content}, ...]
        """
        search_response = []

        try:
            # Determine the format and extract the results list
            items_to_process = []

            # Format 1: Direct list of results (common in self-hosted servers)
            if isinstance(results, list):
                items_to_process = results

            # Format 2: Dict with success/data structure (official Firecrawl API)
            elif isinstance(results, dict):
                # Check for success flag if present
                if "success" in results and not results.get("success", False):
                    print(f"Firecrawl search was not successful: {results}")
                    return search_response

                data = results.get("data", results)

                # Data could be a list directly
                if isinstance(data, list):
                    items_to_process = data
                # Or a dict with 'web' key
                elif isinstance(data, dict):
                    items_to_process = data.get("web", []) or data.get("results", [])
                    # If still empty, try using data values if they look like results
                    if not items_to_process and data:
                        # Maybe the results are at the top level
                        if "url" in data or "href" in data:
                            items_to_process = [data]

            if not items_to_process:
                self.logger.warning(
                    "[Firecrawl] No results found. Raw keys: %s",
                    list(results.keys()) if isinstance(results, dict) else type(results),
                )
                return search_response

            # Process each result
            for item in items_to_process:
                if not isinstance(item, dict):
                    continue

                # Handle different response formats (with or without scraping)
                url = item.get("url") or item.get("href") or item.get("link")

                # Get content - prefer markdown, fall back to description/content/snippet
                content = (
                    item.get("markdown", "") or
                    item.get("content", "") or
                    item.get("description", "") or
                    item.get("snippet", "") or
                    item.get("text", "")
                )

                if url and content:
                    search_response.append({
                        "href": url,
                        "body": content
                    })
                elif url:
                    # If we have URL but no content, at least include the title/description
                    title = item.get("title", "")
                    description = item.get("description", "") or item.get("snippet", "")
                    if title or description:
                        search_response.append({
                            "href": url,
                            "body": f"{title}\n\n{description}" if title else description
                        })

            self.logger.info("[Firecrawl] processed %s results", len(search_response))
            return search_response

        except Exception as e:
            self.logger.exception("Error processing Firecrawl results: %s", e)
            return search_response

