# AI Dev Tools Zoomcamp 2025 - MCP Project

## Homework Questions

### Question 1: Create a New Project

1. Install `uv` for dependency management:
   ```bash
   pip install uv
   ```

2. Create a new directory and initialize the project:
   ```bash
   mkdir mcp_project
   cd mcp_project
   uv init
   ```

3. Install fastmcp:
   ```bash
   uv add fastmcp
   ```

4. The first hash in the `wheels` section of `fastmcp` in `uv.lock` is:
   
   (Note: The actual hash will be visible after running the above commands and checking the `uv.lock` file)

### Question 2: FastMCP Transport

1. Create a `main.py` file with the following content:
   ```python
   from fastmcp import FastMCP

   mcp = FastMCP("Demo 🚀")

   @mcp.tool
   def add(a: int, b: int) -> int:
       """Add two numbers together."""
       return a + b

   if __name__ == "__main__":
       mcp.run()
   ```

2. Run the server:
   ```bash
   python main.py
   ```

3. The server will be available at `http://localhost:8000`

## Project Structure

```
mcp_project/
├── main.py            # Main FastMCP application
├── requirements.txt   # Project dependencies
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## Next Steps

1. Select a GitHub repository with documentation
2. Download the repository data
3. Implement search functionality
4. Test the MCP server with the documentation
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
