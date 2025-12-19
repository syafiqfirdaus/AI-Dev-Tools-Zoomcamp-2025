import requests

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

if __name__ == "__main__":
    # Test the function with the specified URL
    test_url = "https://github.com/alexeygrigorev/minsearch"
    content = scrape_webpage(test_url)
    
    # Print the number of characters in the response
    print(f"Number of characters in the response: {len(content)}")
