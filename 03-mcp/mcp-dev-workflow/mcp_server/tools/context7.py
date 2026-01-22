"""
Context7 integration for live documentation access.
Provides library search and documentation retrieval capabilities.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import httpx

from mcp_server.core.protocol import ToolResult, ToolSchema
from mcp_server.tools.base import Tool


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class Library:
    """Represents a library in Context7."""
    name: str
    version: str
    description: str
    documentation_status: str
    last_updated: Optional[str] = None


@dataclass
class Documentation:
    """Represents documentation content from Context7."""
    library: str
    version: str
    content: str
    format: str
    last_updated: str


@dataclass
class CodeExample:
    """Represents a code example from Context7."""
    library: str
    topic: str
    code: str
    description: str
    language: str


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[datetime] = []
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request.
        Blocks if rate limit would be exceeded.
        """
        now = datetime.now()
        
        # Remove old requests outside the time window
        cutoff = now - timedelta(seconds=self.time_window)
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]
        
        # Check if we're at the limit
        if len(self.requests) >= self.max_requests:
            # Calculate how long to wait
            oldest_request = min(self.requests)
            wait_time = (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds()
            
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.requests.append(now)


class Context7Client:
    """Client for Context7 API integration."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.context7.com"):
        """
        Initialize Context7 client.
        
        Args:
            api_key: Context7 API key
            base_url: Base URL for Context7 API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.rate_limiter = RateLimiter(max_requests=50, time_window=60)  # Conservative rate limit
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "MCP-Dev-Workflow/0.1.0"
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to Context7 API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            retries: Number of retry attempts
            
        Returns:
            Response data as dictionary
            
        Raises:
            httpx.HTTPError: For HTTP errors
            ValueError: For authentication or API errors
        """
        await self.rate_limiter.acquire()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data if data else None
                )
                
                # Handle authentication errors
                if response.status_code == 401:
                    raise ValueError(
                        "Authentication failed. Please check your Context7 API key. "
                        "Ensure the key is valid and has the necessary permissions."
                    )
                
                # Handle rate limiting
                if response.status_code == 429:
                    if attempt < retries:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"Rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        raise ValueError(
                            "Rate limit exceeded. Please try again later or "
                            "reduce the frequency of requests."
                        )
                
                # Handle other HTTP errors
                response.raise_for_status()
                
                # Parse response
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"content": response.text}
                
            except httpx.TimeoutException:
                if attempt < retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request timeout, retrying in {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise ValueError(
                        "Request timed out after multiple attempts. "
                        "Context7 service may be temporarily unavailable."
                    )
            
            except httpx.ConnectError:
                if attempt < retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection error, retrying in {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise ValueError(
                        "Unable to connect to Context7 service. "
                        "Please check your internet connection and try again."
                    )
        
        raise ValueError("Maximum retry attempts exceeded")
    
    async def search_libraries(self, query: str, limit: int = 20) -> List[Library]:
        """
        Search for libraries in Context7.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of Library objects matching the query
            
        Raises:
            ValueError: For API errors or invalid parameters
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        try:
            response_data = await self._make_request(
                method="GET",
                endpoint="/v1/libraries/search",
                params={
                    "q": query.strip(),
                    "limit": limit,
                    "include_status": True
                }
            )
            
            libraries = []
            for lib_data in response_data.get("libraries", []):
                library = Library(
                    name=lib_data.get("name", ""),
                    version=lib_data.get("version", "unknown"),
                    description=lib_data.get("description", ""),
                    documentation_status=lib_data.get("documentation_status", "unknown"),
                    last_updated=lib_data.get("last_updated")
                )
                libraries.append(library)
            
            return libraries
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Library search failed: {str(e)}")
    
    async def get_documentation(self, library: str, version: str = "latest") -> Documentation:
        """
        Retrieve documentation for a specific library.
        
        Args:
            library: Library name
            version: Library version (default: "latest")
            
        Returns:
            Documentation object with content
            
        Raises:
            ValueError: For API errors or invalid parameters
        """
        if not library or not library.strip():
            raise ValueError("Library name cannot be empty")
        
        if not version or not version.strip():
            version = "latest"
        
        try:
            response_data = await self._make_request(
                method="GET",
                endpoint=f"/v1/libraries/{library.strip()}/docs",
                params={
                    "version": version.strip(),
                    "format": "markdown"
                }
            )
            
            documentation = Documentation(
                library=library.strip(),
                version=response_data.get("version", version),
                content=response_data.get("content", ""),
                format=response_data.get("format", "markdown"),
                last_updated=response_data.get("last_updated", datetime.now().isoformat())
            )
            
            return documentation
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Documentation retrieval failed for {library}: {str(e)}")
    
    async def get_examples(self, library: str, topic: str, limit: int = 10) -> List[CodeExample]:
        """
        Get code examples for specific topics in a library.
        
        Args:
            library: Library name
            topic: Topic or functionality to get examples for
            limit: Maximum number of examples to return
            
        Returns:
            List of CodeExample objects
            
        Raises:
            ValueError: For API errors or invalid parameters
        """
        if not library or not library.strip():
            raise ValueError("Library name cannot be empty")
        
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")
        
        if limit <= 0 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")
        
        try:
            response_data = await self._make_request(
                method="GET",
                endpoint=f"/v1/libraries/{library.strip()}/examples",
                params={
                    "topic": topic.strip(),
                    "limit": limit
                }
            )
            
            examples = []
            for example_data in response_data.get("examples", []):
                example = CodeExample(
                    library=library.strip(),
                    topic=topic.strip(),
                    code=example_data.get("code", ""),
                    description=example_data.get("description", ""),
                    language=example_data.get("language", "python")
                )
                examples.append(example)
            
            return examples
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Examples retrieval failed for {library}/{topic}: {str(e)}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection and authentication with Context7.
        
        Returns:
            Dictionary with connection status and user info
            
        Raises:
            ValueError: For authentication or connection errors
        """
        try:
            response_data = await self._make_request(
                method="GET",
                endpoint="/v1/user/profile"
            )
            
            return {
                "status": "connected",
                "user": response_data.get("user", {}),
                "api_version": response_data.get("api_version", "unknown"),
                "rate_limit": response_data.get("rate_limit", {})
            }
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Connection test failed: {str(e)}")


class Context7SearchTool(Tool):
    """MCP tool for searching libraries in Context7."""
    
    def __init__(self, context7_client: Context7Client):
        """Initialize Context7 search tool."""
        super().__init__(
            name="context7_search_libraries",
            description="Search for libraries in Context7 documentation service"
        )
        self.context7_client = context7_client
    
    def get_schema(self) -> ToolSchema:
        """Get the tool's schema definition."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for libraries (e.g., 'fastapi', 'machine learning', 'web framework')",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the library search tool."""
        try:
            # Validate arguments
            schema = self.get_schema().input_schema
            self._validate_arguments(arguments, schema)
            
            query = arguments["query"]
            limit = arguments.get("limit", 20)
            
            # Search libraries
            libraries = await self.context7_client.search_libraries(query, limit)
            
            if not libraries:
                return self._create_text_result(
                    f"No libraries found for query: '{query}'. "
                    "Try using different keywords or check the spelling."
                )
            
            # Format results
            result_text = f"Found {len(libraries)} libraries for '{query}':\n\n"
            
            for i, lib in enumerate(libraries, 1):
                result_text += f"{i}. **{lib.name}** (v{lib.version})\n"
                result_text += f"   Description: {lib.description}\n"
                result_text += f"   Documentation Status: {lib.documentation_status}\n"
                if lib.last_updated:
                    result_text += f"   Last Updated: {lib.last_updated}\n"
                result_text += "\n"
            
            return self._create_text_result(result_text)
            
        except ValueError as e:
            return self._create_error_result(str(e))
        except Exception as e:
            return self._create_error_result(f"Library search error: {str(e)}")


class Context7DocumentationTool(Tool):
    """MCP tool for retrieving documentation from Context7."""
    
    def __init__(self, context7_client: Context7Client):
        """Initialize Context7 documentation tool."""
        super().__init__(
            name="context7_get_documentation",
            description="Retrieve documentation for a specific library from Context7"
        )
        self.context7_client = context7_client
    
    def get_schema(self) -> ToolSchema:
        """Get the tool's schema definition."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "library": {
                        "type": "string",
                        "description": "Name of the library to get documentation for",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "version": {
                        "type": "string",
                        "description": "Version of the library (default: 'latest')",
                        "default": "latest"
                    }
                },
                "required": ["library"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the documentation retrieval tool."""
        try:
            # Validate arguments
            schema = self.get_schema().input_schema
            self._validate_arguments(arguments, schema)
            
            library = arguments["library"]
            version = arguments.get("version", "latest")
            
            # Get documentation
            documentation = await self.context7_client.get_documentation(library, version)
            
            # Format results
            result_text = f"# Documentation for {documentation.library} (v{documentation.version})\n\n"
            result_text += f"**Format:** {documentation.format}\n"
            result_text += f"**Last Updated:** {documentation.last_updated}\n\n"
            result_text += "## Content\n\n"
            result_text += documentation.content
            
            return self._create_text_result(result_text)
            
        except ValueError as e:
            return self._create_error_result(str(e))
        except Exception as e:
            return self._create_error_result(f"Documentation retrieval error: {str(e)}")


class Context7ExamplesTool(Tool):
    """MCP tool for retrieving code examples from Context7."""
    
    def __init__(self, context7_client: Context7Client):
        """Initialize Context7 examples tool."""
        super().__init__(
            name="context7_get_examples",
            description="Get code examples for specific topics in a library from Context7"
        )
        self.context7_client = context7_client
    
    def get_schema(self) -> ToolSchema:
        """Get the tool's schema definition."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            input_schema={
                "type": "object",
                "properties": {
                    "library": {
                        "type": "string",
                        "description": "Name of the library to get examples for",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "topic": {
                        "type": "string",
                        "description": "Topic or functionality to get examples for (e.g., 'authentication', 'routing', 'database')",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of examples to return",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 10
                    }
                },
                "required": ["library", "topic"],
                "additionalProperties": False
            }
        )
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Execute the examples retrieval tool."""
        try:
            # Validate arguments
            schema = self.get_schema().input_schema
            self._validate_arguments(arguments, schema)
            
            library = arguments["library"]
            topic = arguments["topic"]
            limit = arguments.get("limit", 10)
            
            # Get examples
            examples = await self.context7_client.get_examples(library, topic, limit)
            
            if not examples:
                return self._create_text_result(
                    f"No examples found for '{topic}' in {library}. "
                    "Try using different topic keywords or check if the library is available."
                )
            
            # Format results
            result_text = f"# Code Examples for {library} - {topic}\n\n"
            result_text += f"Found {len(examples)} examples:\n\n"
            
            for i, example in enumerate(examples, 1):
                result_text += f"## Example {i}: {example.description}\n\n"
                result_text += f"**Language:** {example.language}\n\n"
                result_text += f"```{example.language}\n{example.code}\n```\n\n"
            
            return self._create_text_result(result_text)
            
        except ValueError as e:
            return self._create_error_result(str(e))
        except Exception as e:
            return self._create_error_result(f"Examples retrieval error: {str(e)}")