# AI Dev Tools Zoomcamp 2025 - MCP Homework

This project implements a FastMCP server with documentation search capabilities, completing the homework requirements for Module 3.

## Project Overview

This MCP server provides:

- Web scraping using Jina Reader
- Word counting on web pages
- FastMCP documentation search using minsearch

## Homework Answers

### Question 1: Create a New Project

**Setup:**

```bash
pip install uv
uv init
uv add fastmcp minsearch requests
```

**Answer:** The first hash in the `wheels` section of `fastmcp` in `uv.lock` is:

```
sha256:fb3e365cc1d52573ab89caeba9944dd4b056149097be169bce428e011f0a57e5
```

### Question 2: FastMCP Transport

**Answer:** STDIO

The server uses STDIO (Standard Input/Output) as the transport mechanism for MCP communication.

### Question 3: Scrape Web Tool

**Implementation:** See `web_scraper.py` for the standalone implementation, or `main.py` for the integrated version.

The `scrape_webpage()` function uses Jina Reader by prepending `https://r.jina.ai/` to any URL.

**Answer:** Approximately **19184** characters (may vary slightly depending on when the page was scraped)

### Question 4: Integrate the Tool

The `count_word_occurrences()` tool is implemented as an MCP tool in `main.py`.

**Running the server:**

```bash
uv --directory /full/path/to/mcp_project run python main.py
```

**Answer:** The word "data" appears approximately **111** times on <https://datatalks.club/> (may vary as the website content changes)

### Question 5: Implement Search

**Implementation:** See `search.py`

The search implementation:

- Downloads the FastMCP repository from GitHub
- Extracts and indexes all `.md` and `.mdx` files
- Removes the "fastmcp-main/" prefix from paths
- Uses `minsearch` for document indexing and search
- Returns the top 5 most relevant documents

**Answer:** `examples/testing_demo/README.md`

**Testing the search:**

```bash
uv run python search.py
```

### Question 6: Search Tool (Ungraded)

The search functionality is integrated as an MCP tool in `main.py` via the `search_fastmcp_docs()` function.

**Features:**

- Lazy loading of the search index (loads on first use)
- Configurable number of results (1-10)
- Returns formatted results with file names, previews, and full content

## Project Structure

```
mcp_project/
├── main.py              # Main FastMCP server with all tools
├── search.py            # Standalone search implementation
├── web_scraper.py       # Standalone web scraper
├── test_word_count.py   # Test file for word counting
├── pyproject.toml       # Project dependencies
├── uv.lock             # Dependency lock file (for Question 1)
├── requirements.txt     # Alternative dependency list
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Installation

1. Install `uv`:

   ```bash
   pip install uv
   ```

2. Install dependencies:

   ```bash
   cd mcp_project
   uv add fastmcp minsearch requests
   ```

## Usage

### Running the MCP Server

Start the FastMCP server:

```bash
uv run python main.py
```

### Running Standalone Scripts

**Test web scraping:**

```bash
uv run python web_scraper.py
```

**Test word counting:**

```bash
uv run python test_word_count.py
```

**Test documentation search:**

```bash
uv run python search.py
```

## MCP Tools Available

1. **add** - Add two numbers (demo tool)
   - Parameters: `a: int, b: int`
   - Returns: `int`

2. **count_word_occurrences** - Count word occurrences on a webpage
   - Parameters: `url: str, word: str`
   - Returns: `Dict` with count and metadata

3. **search_fastmcp_docs** - Search FastMCP documentation
   - Parameters: `query: str, num_results: int = 5`
   - Returns: `List[Dict]` with search results

## Integration with AI Assistants

To use this MCP server with your AI assistant:

1. Add to your MCP configuration (e.g., for Claude Desktop or VSCode):

   ```json
   {
     "mcpServers": {
       "fastmcp-docs": {
         "command": "uv",
         "args": [
           "--directory",
           "/full/path/to/mcp_project",
           "run",
           "python",
           "main.py"
         ]
       }
     }
   }
   ```

2. Restart your AI assistant

3. The MCP tools will be available for use

## Technologies Used

- **FastMCP**: Framework for building MCP servers
- **minsearch**: Lightweight text search engine with TF-IDF
- **Jina Reader**: Web content extraction service
- **uv**: Fast Python package manager

## Notes

- The search index is lazy-loaded on first use to improve startup time
- Downloaded documentation is cached in `.cache/` directory
- All paths are normalized to use forward slashes
- The "fastmcp-main/" prefix is automatically removed from file paths

## License

This project is part of the AI Dev Tools Zoomcamp 2025 homework.
