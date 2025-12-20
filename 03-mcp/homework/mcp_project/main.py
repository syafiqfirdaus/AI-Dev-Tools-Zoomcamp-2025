import requests
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from pathlib import Path
import minsearch

# Import search utilities
from search import download_file, extract_zip, find_markdown_files, process_file, REPO_URL, ZIP_PATH, EXTRACT_DIR, CACHE_DIR

mcp = FastMCP("FastMCP Documentation Search 🚀")

# Global index for documentation search (lazy loaded)
_search_index: Optional[minsearch.Index] = None

def initialize_search_index() -> minsearch.Index:
    """Initialize the search index if not already loaded."""
    global _search_index
    
    if _search_index is not None:
        return _search_index
    
    print("Initializing search index...")
    
    # Download and extract the repository
    download_file(REPO_URL, ZIP_PATH)
    extract_zip(ZIP_PATH, EXTRACT_DIR)
    
    # Find and process markdown files
    markdown_files = find_markdown_files(EXTRACT_DIR)
    
    # Process files and create documents
    docs = []
    for file_path in markdown_files:
        doc = process_file(file_path, EXTRACT_DIR)
        if doc:
            docs.append(doc)
    
    # Create and fit minsearch index
    index = minsearch.Index(
        text_fields=['content', 'filename'],
        keyword_fields=[]
    )
    index.fit(docs)
    
    _search_index = index
    print(f"Search index initialized with {len(docs)} documents.")
    return _search_index

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def scrape_webpage(url: str) -> str:
    """
    Fetch the content of a web page using Jina reader.
    
    Args:
        url (str): The URL of the web page to scrape
        
    Returns:
        str: The content of the web page in markdown format
    """
    try:
        # Jina reader endpoint
        jina_url = f"https://r.jina.ai/{url}"
        
        # Set headers to indicate we want markdown response
        headers = {
            'Accept': 'text/markdown'
        }
        
        # Make the request
        response = requests.get(jina_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching the URL: {str(e)}"

@mcp.tool
def count_word_occurrences(url: str, word: str) -> Dict[str, Any]:
    """
    Count how many times a word appears on a web page.
    
    Args:
        url (str): The URL of the web page to analyze
        word (str): The word to count
        
    Returns:
        dict: A dictionary containing the count and other information
    """
    content = scrape_webpage(url)
    
    # Convert both the content and the word to lowercase for case-insensitive search
    count = content.lower().count(word.lower())
    
    return {
        "url": url,
        "word": word,
        "count": count,
        "character_count": len(content),
        "status": "success"
    }

@mcp.tool
def search_fastmcp_docs(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the FastMCP documentation for relevant information.
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return (default: 5, max: 10)
        
    Returns:
        List[Dict]: A list of search results with filename and content preview
    """
    # Limit num_results
    num_results = min(max(1, num_results), 10)
    
    # Initialize index if needed
    index = initialize_search_index()
    
    # Perform search
    results = index.search(
        query=query,
        filter_dict={},
        boost_dict={'filename': 2.0, 'content': 1.0},
        num_results=num_results
    )
    
    # Format results for better readability
    formatted_results = []
    for i, result in enumerate(results, 1):
        filename = result.get('filename', 'Unknown')
        content = result.get('content', '')
        # Get first 300 characters as preview
        preview = content[:300].replace('\n', ' ').strip()
        
        formatted_results.append({
            'rank': i,
            'filename': filename,
            'preview': preview + '...' if len(content) > 300 else preview,
            'full_content': content
        })
    
    return formatted_results

if __name__ == "__main__":
    mcp.run()
