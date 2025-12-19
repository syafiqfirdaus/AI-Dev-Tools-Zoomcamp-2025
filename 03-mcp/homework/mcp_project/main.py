import requests
from typing import Dict, Any
from fastmcp import FastMCP

mcp = FastMCP("Web Scraper Tool 🕷️")

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

if __name__ == "__main__":
    mcp.run()
