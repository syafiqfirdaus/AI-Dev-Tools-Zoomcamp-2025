# MCP Project

This is the MCP project for the AI Dev Tools Zoomcamp 2025.

## Project Structure

- `main.py`: Main script file
- `requirements.txt`: Project dependencies
- `.gitignore`: Git ignore file

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python main.py
```
This will analyze the default webpage (Python Wikipedia page) and show the top 10 most common words.

### Advanced Usage
```bash
python main.py [URL] [options]
```

### Options:
- `URL`: Webpage URL to analyze (default: Python Wikipedia page)
- `-n, --top-n N`: Show top N words (default: 10)
- `-o, --output FILE`: Save results to a JSON file
- `--no-stop-words`: Exclude common English stop words

### Examples:
1. Analyze a specific URL:
   ```bash
   python main.py https://en.wikipedia.org/wiki/Artificial_intelligence
   ```

2. Show top 20 words and save to file:
   ```bash
   python main.py -n 20 -o results.json
   ```

3. Exclude common stop words:
   ```bash
   python main.py --no-stop-words
   ```

## Output

The script displays:
- Top N most common words
- Total number of unique words
- Total word count

When using the `-o/--output` option, results are saved in JSON format with the following structure:
```json
{
  "top_words": [
    {"word": "example", "count": 123}
  ],
  "total_unique_words": 1000,
  "total_words": 5000
}
```

## Dependencies

- Python 3.6+
- requests
- beautifulsoup4

## License

This project is licensed under the MIT License.
