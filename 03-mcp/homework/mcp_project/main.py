import requests
from bs4 import BeautifulSoup
import re
import argparse
import json
from collections import Counter
from pathlib import Path

# Common English stop words
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
    'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
    "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't",
    'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
    'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def fetch_webpage(url):
    """Fetch the content of a webpage with proper headers."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

def extract_text(html_content):
    """Extract text from HTML content."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    # Get text
    text = soup.get_text()
    # Break into lines and remove leading/trailing whitespace
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def count_words(text):
    """Count the frequency of each word in the text."""
    if not text:
        return Counter()
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Count word frequencies
    return Counter(words)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Web scraper that counts word frequencies from a webpage.')
    parser.add_argument('url', nargs='?', default='https://en.wikipedia.org/wiki/Python_(programming_language)',
                      help='URL of the webpage to analyze (default: Python Wikipedia page)')
    parser.add_argument('-n', '--top-n', type=int, default=10,
                      help='Number of top words to display (default: 10)')
    parser.add_argument('-o', '--output', type=str,
                      help='Output file to save results (JSON format)')
    parser.add_argument('--no-stop-words', action='store_true',
                      help='Exclude common English stop words')
    return parser.parse_args()

def filter_stop_words(word_counter):
    """Filter out common English stop words from the counter."""
    return Counter({k: v for k, v in word_counter.items() if k.lower() not in STOP_WORDS})

def save_results(word_counts, top_n, output_file):
    """Save results to a JSON file."""
    result = {
        'top_words': [{'word': w, 'count': c} for w, c in word_counts.most_common(top_n)],
        'total_unique_words': len(word_counts),
        'total_words': sum(word_counts.values())
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_file}")
    except IOError as e:
        print(f"\nError saving to file: {e}")

def main():
    args = parse_arguments()
    
    print(f"Fetching content from: {args.url}")
    
    # Fetch and process the webpage
    html_content = fetch_webpage(args.url)
    if not html_content:
        return
        
    text_content = extract_text(html_content)
    word_counts = count_words(text_content)
    
    # Filter out stop words if requested
    if args.no_stop_words:
        word_counts = filter_stop_words(word_counts)
    
    # Get top N words
    top_words = word_counts.most_common(args.top_n)
    
    # Print results
    print(f"\nTop {args.top_n} most common words:")
    print("-" * 30)
    for word, count in top_words:
        print(f"{word}: {count}")
    
    print("\nStatistics:")
    print("-" * 30)
    print(f"Total unique words: {len(word_counts):,}")
    print(f"Total words: {sum(word_counts.values()):,}")
    
    # Save to file if output path is provided
    if args.output:
        save_results(word_counts, args.top_n, args.output)

if __name__ == "__main__":
    main()
