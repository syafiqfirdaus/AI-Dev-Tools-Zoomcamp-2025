import os
import re
import zipfile
import requests
import shutil
import difflib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

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

def process_file(file_path: Path) -> Optional[Dict[str, str]]:
    """Process a markdown file and return its content and metadata."""
    # Get the relative path
    rel_path = file_path.relative_to(EXTRACT_DIR)
    
    # Skip files in certain directories
    if any(part.startswith('_') for part in rel_path.parts):
        return None
    
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None
    
    return {
        'path': str(rel_path),
        'filename': str(rel_path.name),
        'content': content
    }

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two strings."""
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def search_docs(query: str, docs: List[Dict[str, str]], limit: int = 5) -> List[Dict[str, Any]]:
    """Search for documents matching the query using fuzzy matching."""
    results = []
    
    for doc in docs:
        # Calculate score based on both filename and content
        filename_score = calculate_similarity(query, doc['filename'])
        content_score = calculate_similarity(query, doc['content'])
        
        # Weight filename matches higher than content matches
        total_score = (filename_score * 2 + content_score) / 3
        
        if total_score > 0.1:  # Only include results with a minimum similarity
            results.append({
                'path': doc['path'],
                'filename': doc['filename'],
                'score': total_score,
                'content': doc['content'][:200] + '...'  # Return a snippet
            })
    
    # Sort by score in descending order
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top N results
    return results[:limit]

def main():
    # Download and extract the repository
    print("Setting up the documentation...")
    download_file(REPO_URL, ZIP_PATH)
    extract_zip(ZIP_PATH, EXTRACT_DIR)
    
    # Find and process markdown files
    print("Processing markdown files...")
    markdown_files = find_markdown_files(EXTRACT_DIR)
    print(f"Found {len(markdown_files)} markdown files.")
    
    # Process files and create documents
    docs = []
    for file_path in markdown_files:
        doc = process_file(file_path)
        if doc:
            docs.append(doc)
    
    print(f"Processed {len(docs)} documents.")
    
    # Test search
    test_query = "demo"
    print(f"\nSearching for: {test_query}")
    results = search_docs(test_query, docs)
    
    # Print results
    print(f"\nTop {len(results)} results for '{test_query}':")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['path']} (score: {result['score']:.2f})")
        print(f"   {result['content']}\n")

if __name__ == "__main__":
    main()
