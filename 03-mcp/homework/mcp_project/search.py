import os
import zipfile
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
import minsearch

# Constants
REPO_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"
CACHE_DIR = Path(".cache")
ZIP_PATH = CACHE_DIR / "fastmcp-main.zip"
EXTRACT_DIR = CACHE_DIR / "fastmcp-main"

def download_file(url: str, path: Path) -> bool:
    """Download a file from a URL if it doesn't exist."""
    if path.exists():
        print(f"File already exists: {path}")
        return True
    
    print(f"Downloading {url}...")
    os.makedirs(path.parent, exist_ok=True)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract a zip file if the target directory doesn't exist."""
    if extract_to.exists():
        print(f"Directory already exists: {extract_to}")
        return True
    
    print(f"Extracting {zip_path} to {extract_to}...")
    os.makedirs(extract_to, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to.parent)
        return True
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")
        return False

def find_markdown_files(directory: Path) -> List[Path]:
    """Find all markdown files in a directory recursively."""
    markdown_files = []
    for ext in ('*.md', '*.mdx'):
        markdown_files.extend(directory.rglob(ext))
    return markdown_files

def process_file(file_path: Path, extract_dir: Path) -> Optional[Dict[str, str]]:
    """Process a markdown file and return its content and metadata."""
    # Get the relative path
    rel_path = file_path.relative_to(extract_dir)
    
    # Skip files in directories starting with underscore
    if any(part.startswith('_') for part in rel_path.parts):
        return None
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    
    # Convert path to string and remove the "fastmcp-main/" prefix
    path_str = str(rel_path)
    if path_str.startswith('fastmcp-main/'):
        path_str = path_str[13:]  # Remove "fastmcp-main/" (13 characters)
    elif path_str.startswith('fastmcp-main\\'):
        path_str = path_str[13:]  # Remove "fastmcp-main\" on Windows
    
    # Replace backslashes with forward slashes for consistency
    path_str = path_str.replace('\\', '/')
    
    return {
        'filename': path_str,
        'content': content
    }

def search_docs(query: str, index: minsearch.Index, num_results: int = 5) -> List[Dict[str, Any]]:
    """Search for documents matching the query using minsearch."""
    results = index.search(
        query=query,
        filter_dict={},
        boost_dict={'filename': 2.0, 'content': 1.0},
        num_results=num_results
    )
    return results

def main():
    # Download and extract the repository
    print("Setting up the documentation...")
    download_file(REPO_URL, ZIP_PATH)
    extract_zip(ZIP_PATH, EXTRACT_DIR)
    
    # Find and process markdown files
    print("\nProcessing markdown files...")
    markdown_files = find_markdown_files(EXTRACT_DIR)
    print(f"Found {len(markdown_files)} markdown files.")
    
    # Process files and create documents
    docs = []
    for file_path in markdown_files:
        doc = process_file(file_path, EXTRACT_DIR)
        if doc:
            docs.append(doc)
    
    print(f"Processed {len(docs)} documents.")
    
    # Create and fit minsearch index
    print("\nIndexing documents with minsearch...")
    index = minsearch.Index(
        text_fields=['content', 'filename'],
        keyword_fields=[]
    )
    index.fit(docs)
    print("Indexing complete!")
    
    # Test search
    test_query = "demo"
    print(f"\n{'='*60}")
    print(f"Searching for: '{test_query}'")
    print(f"{'='*60}")
    results = search_docs(test_query, index)
    
    # Print results
    print(f"\nTop {len(results)} results for '{test_query}':")
    print(f"{'-'*60}")
    for i, result in enumerate(results, 1):
        filename = result.get('filename', 'Unknown')
        content_preview = result.get('content', '')[:150].replace('\n', ' ')
        print(f"{i}. {filename}")
        print(f"   Preview: {content_preview}...")
        print()

if __name__ == "__main__":
    main()
