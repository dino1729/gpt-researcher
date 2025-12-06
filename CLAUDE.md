# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GPT Researcher is an autonomous AI research agent that conducts comprehensive web and local document research on any topic, generating detailed reports with citations. The system uses a multi-agent architecture with LangChain/LangGraph for orchestrating specialized research workflows.

**Key Capabilities:**
- Autonomous research planning and execution with parallel agent processing
- Multi-source data aggregation (web scraping, academic papers, local documents)
- Multiple report types: research reports, detailed reports, subtopic reports, deep research
- MCP (Model Context Protocol) integration for custom data sources
- Multi-agent system using LangGraph for complex research workflows
- Support for multiple LLM providers (OpenAI, Anthropic, local models via Ollama/LiteLLM)

## Architecture

### Core Components

**GPTResearcher (`gpt_researcher/agent.py`)**: Main research orchestrator that coordinates the research workflow. Initializes with query, report type, and configuration, then manages the research lifecycle.

**Research Skills (`gpt_researcher/skills/`)**:
- `ResearchConductor`: Orchestrates research execution
- `ReportGenerator`: Writes final reports
- `BrowserManager`: Web content retrieval
- `SourceCurator`: Validates and filters sources
- `ContextManager`: Manages research context
- `DeepResearchSkill`: Recursive tree-like research exploration

**Actions (`gpt_researcher/actions/`)**: Discrete research operations like search, scraping, source selection, and content extraction.

**Retrievers (`gpt_researcher/retrievers/`)**: Search interfaces for Firecrawl, Arxiv, and MCP servers. Retriever selection is configured via `RETRIEVER` environment variable (e.g., `RETRIEVER=firecrawl,mcp`).

**Multi-Agent System (`multi_agents/`)**: LangGraph-based team of specialized agents:
- **Chief Editor**: Coordinates the agent team
- **Browser**: Initial topic research
- **Editor**: Plans report structure and outlines
- **Researcher**: In-depth research on subtopics
- **Reviewer**: Validates research quality
- **Revisor**: Improves drafts based on feedback
- **Writer**: Compiles final report
- **Publisher**: Exports to PDF/DOCX/Markdown

### Backend Server

**FastAPI Application (`backend/server/app.py`)**:
- Serves static frontend and REST/WebSocket APIs
- Handles research requests, file uploads, and chat interactions
- WebSocket manager for streaming research progress
- No database persistence - outputs saved to filesystem

**Frontend**:
- Static HTML/CSS/JS served by FastAPI (`frontend/`) - Single-page application with vanilla JavaScript

## Development Commands

### Setup and Installation

```bash
# Install Python dependencies (Python 3.11+ required)
pip install -r requirements.txt

# Or use Poetry
poetry install

# Configure API keys - copy and edit .env file
cp .env.example .env
# Required: OPENAI_API_KEY or ANTHROPIC_API_KEY
# Required: FIRECRAWL_API_KEY (for web search)
```

### Running the Application

```bash
# Start FastAPI server with auto-reload (development)
python -m uvicorn main:app --reload

# Start server without reload (production)
python -m uvicorn main:app --host=0.0.0.0 --port=8000

# Or run directly
python main.py

# Run as PIP package (programmatic usage)
python
>>> from gpt_researcher import GPTResearcher
>>> researcher = GPTResearcher(query="your research topic")
>>> await researcher.conduct_research()
>>> report = await researcher.write_report()
```

### Multi-Agent Research

```bash
# Navigate to multi_agents directory
cd multi_agents

# Edit task.json to configure research query and settings
# Then run multi-agent research
python main.py

# Outputs generated in multi_agents/outputs/ directory
```

### Testing

```bash
# Run Python tests
python -m pytest tests/

# Test specific components
python tests/test-your-llm.py          # Test LLM configuration
python tests/test-your-embeddings.py   # Test embeddings
python tests/test-your-retriever.py    # Test search retriever
python tests/test_mcp.py              # Test MCP integration

# Run tests in Docker
docker-compose run gpt-researcher-tests
```

### Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Configuration

### Environment Variables

Key environment variables (see `.env.example` for all options):

```bash
# LLM Provider Selection
LLM_PROVIDER=openai          # Options: openai, anthropic, ollama, litellm
FAST_LLM_MODEL=gpt-4o-mini   # For quick operations
SMART_LLM_MODEL=gpt-4o       # For complex reasoning
STRATEGIC_LLM_MODEL=gpt-4o   # For planning

# API Keys
OPENAI_API_KEY=              # OpenAI API key
ANTHROPIC_API_KEY=           # Anthropic API key
FIRECRAWL_API_KEY=           # Firecrawl search API key

# Local LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_FAST_LLM=llama2
OLLAMA_SMART_LLM=mixtral

# LiteLLM (unified interface)
LITELLM_BASE_URL=
LITELLM_API_KEY=
LITELLM_FAST_LLM=
LITELLM_SMART_LLM=

# Search Configuration
RETRIEVER=firecrawl          # Options: firecrawl, arxiv, mcp (comma-separated)
MAX_SEARCH_RESULTS_PER_QUERY=5

# Local Document Research
DOC_PATH=./my-docs          # Path to local documents for research

# MCP Configuration (passed in code, not env)
# Configure MCP servers via mcp_configs parameter in GPTResearcher constructor
```

### Report Types

- `research_report`: Standard comprehensive research
- `detailed_report`: Section-by-section detailed analysis
- `subtopic_report`: Focused research on specific subtopics
- `deep_research`: Recursive exploration with configurable depth/breadth

### LLM Provider Configuration

The system uses three model tiers:
- **FAST_LLM**: Quick operations, simple tasks (e.g., extraction, formatting)
- **SMART_LLM**: Complex reasoning, research analysis
- **STRATEGIC_LLM**: High-level planning, coordination

Configure via environment variables with `{PROVIDER}_` prefix (e.g., `OPENAI_SMART_LLM`, `OLLAMA_FAST_LLM`).

## MCP Integration

Model Context Protocol enables research from custom data sources (GitHub, databases, APIs):

```python
from gpt_researcher import GPTResearcher
import os

# Enable MCP alongside web search
os.environ["RETRIEVER"] = "firecrawl,mcp"

researcher = GPTResearcher(
    query="Research query",
    mcp_configs=[
        {
            "name": "github",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")}
        }
    ]
)
```

## Important Implementation Details

### Research Workflow
1. Query is analyzed and agent role is selected
2. Initial search generates research questions
3. Parallel execution: multiple retrievers fetch content simultaneously
4. Content is scraped, processed, and stored in context
5. Sources are validated and curated
6. Report is generated using accumulated context
7. References and citations are added

### WebSocket Communication
The FastAPI server uses WebSockets for real-time research progress streaming. Key events: `logs`, `path`, `report`, `sources`. See `backend/server/websocket_manager.py` for implementation.

### Document Processing
Supports PDF, DOCX, TXT, CSV, Excel, Markdown, PowerPoint via `unstructured` library. Documents in `DOC_PATH` are automatically indexed when `report_source=local`.

### Vector Store
Uses in-memory vector store with configurable embeddings for semantic document retrieval. Context management ensures relevant information is surfaced during research.

### Multi-Agent Coordination
The `multi_agents/` system uses LangGraph's state management and conditional edges for agent orchestration. Each agent has specific responsibilities and hands off to the next agent based on completion criteria.

## Project Structure Notes

- `gpt_researcher/`: Core research engine and utilities
- `backend/`: FastAPI server, WebSocket handlers, utilities
- `frontend/`: Static HTML/CSS/JS frontend (vanilla JavaScript SPA)
- `multi_agents/`: LangGraph multi-agent research system
- `tests/`: Test scripts and examples
- `outputs/`: Generated research reports (JSON format with metadata)
- `logs/`: Application logs

## Development Guidelines

- Follow existing patterns in `gpt_researcher/` for new research skills
- Maintain async/await patterns throughout - all research operations are asynchronous
- WebSocket streaming should send granular updates for better UX
- Add new retrievers in `gpt_researcher/retrievers/` following the base interface
- Test LLM provider changes with `tests/test-your-llm.py`
- For multi-agent changes, test with simplified `task.json` first
- Use type hints extensively - codebase uses Pydantic models for validation
- Handle API rate limits and network failures gracefully with retries

## Common Tasks

**Add a new retriever**: Create class in `gpt_researcher/retrievers/`, implement `search()` method, register in `get_retrievers()` in `actions/__init__.py`.

**Modify report format**: Edit templates in `gpt_researcher/prompts.py` or add custom prompt family.

**Add new agent to multi-agent system**: Create agent in `multi_agents/agents/`, define node function, add to graph in `multi_agents/agent.py`.

**Customize research depth**: Adjust `MAX_ITERATIONS`, `MAX_SEARCH_RESULTS_PER_QUERY` in environment or pass as parameters to `GPTResearcher`.

**Enable Deep Research**: Use `report_type="deep_research"` and configure depth/breadth in constructor.

## Repository URLs

- Homepage: https://gptr.dev/
- Documentation: https://docs.gptr.dev/
- GitHub: https://github.com/assafelovic/gpt-researcher
- MCP Server: https://github.com/assafelovic/gptr-mcp
