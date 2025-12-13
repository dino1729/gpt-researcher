import asyncio
import json
import os
import re
import time
import shutil
import traceback
from typing import Awaitable, Dict, List, Any, Optional
from fastapi.responses import JSONResponse, FileResponse
from gpt_researcher.document.document import DocumentLoader
from gpt_researcher import GPTResearcher
from utils import write_md_to_pdf, write_md_to_word, write_text_to_md
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def apply_llm_provider_mode(
    llm_provider_mode: str,
    ollama_base_url: Optional[str] = None,
    ollama_model: Optional[str] = None,
    ollama_embedding_model: Optional[str] = None,
    litellm_base_url: Optional[str] = None,
    litellm_api_key: Optional[str] = None,
    litellm_model: Optional[str] = None,
    litellm_embedding_model: Optional[str] = None,
) -> None:
    """
    Apply environment variable overrides based on the selected LLM provider mode.
    
    Args:
        llm_provider_mode: Either 'ollama' for local models or 'litellm' for online models :-)
        ollama_base_url: Optional override for the Ollama server URL.
        ollama_model: Optional override for the Ollama model to use for all roles.
        ollama_embedding_model: Optional override for the Ollama embedding model.
        litellm_base_url: Optional override for the LiteLLM server URL.
        litellm_api_key: Optional override for the LiteLLM API key.
        litellm_model: Optional override for the LiteLLM model to use for all roles.
        litellm_embedding_model: Optional override for the LiteLLM embedding model.
    """
    def _with_provider_prefix(provider: str, value: Optional[str]) -> Optional[str]:
        """
        Ensure the value is prefixed with '<provider>:' even if it already contains
        a colon for model variants (e.g., 'qwen3:8b'). We only skip when it is
        already explicitly prefixed with '<provider>:'.
        """
        if not value:
            return None
        if value.startswith(f"{provider}:"):
            return value
        return f"{provider}:{value}"

    if llm_provider_mode == "ollama":
        # Override with Ollama environment variables or request-level overrides
        resolved_base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL")
        if resolved_base_url:
            normalized_base_url = resolved_base_url.rstrip("/")
            os.environ["OLLAMA_BASE_URL"] = normalized_base_url
            os.environ["OPENAI_BASE_URL"] = normalized_base_url
            logger.info(f"Using Ollama base URL: {normalized_base_url}")
        
        # If a specific model was chosen, use it for all roles, otherwise fall back to env vars
        if ollama_model:
            prefixed_model = _with_provider_prefix("ollama", ollama_model)
            os.environ["FAST_LLM"] = prefixed_model
            os.environ["SMART_LLM"] = prefixed_model
            os.environ["STRATEGIC_LLM"] = prefixed_model
            logger.info(f"Using Ollama model for all roles: {prefixed_model}")
        else:
            if os.getenv("OLLAMA_FAST_LLM"):
                prefixed_fast = _with_provider_prefix("ollama", os.getenv("OLLAMA_FAST_LLM"))
                os.environ["FAST_LLM"] = prefixed_fast
                logger.info(f"Using Ollama fast LLM: {prefixed_fast}")
            
            if os.getenv("OLLAMA_SMART_LLM"):
                prefixed_smart = _with_provider_prefix("ollama", os.getenv("OLLAMA_SMART_LLM"))
                os.environ["SMART_LLM"] = prefixed_smart
                logger.info(f"Using Ollama smart LLM: {prefixed_smart}")
            
            if os.getenv("OLLAMA_STRATEGIC_LLM"):
                prefixed_strategic = _with_provider_prefix("ollama", os.getenv("OLLAMA_STRATEGIC_LLM"))
                os.environ["STRATEGIC_LLM"] = prefixed_strategic
                logger.info(f"Using Ollama strategic LLM: {prefixed_strategic}")
        
        # Embedding selection for Ollama: prefer user selection, then env vars
        if ollama_embedding_model:
            prefixed_embedding = _with_provider_prefix("ollama", ollama_embedding_model)
            os.environ["EMBEDDING"] = prefixed_embedding
            logger.info(f"Using Ollama embedding model (user selected): {prefixed_embedding}")
        elif os.getenv("OLLAMA_EMBEDDING"):
            prefixed_embedding = _with_provider_prefix("ollama", os.getenv("OLLAMA_EMBEDDING"))
            os.environ["EMBEDDING"] = prefixed_embedding
            logger.info(f"Using Ollama embedding (from env): {prefixed_embedding}")
    
    elif llm_provider_mode == "litellm":
        # Use LiteLLM proxy as an OpenAI-compatible endpoint
        resolved_base_url = litellm_base_url or os.getenv("LITELLM_BASE_URL")
        if resolved_base_url:
            normalized_base_url = resolved_base_url.rstrip("/")
            os.environ["OPENAI_BASE_URL"] = normalized_base_url
            os.environ["LITELLM_BASE_URL"] = normalized_base_url
            logger.info(f"Using LiteLLM base URL: {normalized_base_url}")
        
        resolved_api_key = litellm_api_key or os.getenv("LITELLM_API_KEY")
        if resolved_api_key:
            os.environ["OPENAI_API_KEY"] = resolved_api_key
            os.environ["LITELLM_API_KEY"] = resolved_api_key
            logger.info("Using LiteLLM API key")

        if litellm_model:
            # Treat LiteLLM proxy as OpenAI-compatible; keep provider 'openai'
            prefixed_model = _with_provider_prefix("openai", litellm_model)
            os.environ["FAST_LLM"] = prefixed_model
            os.environ["SMART_LLM"] = prefixed_model
            os.environ["STRATEGIC_LLM"] = prefixed_model
            logger.info(f"Using LiteLLM model for all roles: {prefixed_model}")
        elif os.getenv("LITELLM_FAST_LLM") or os.getenv("LITELLM_SMART_LLM") or os.getenv("LITELLM_STRATEGIC_LLM"):
            if os.getenv("LITELLM_FAST_LLM"):
                os.environ["FAST_LLM"] = os.getenv("LITELLM_FAST_LLM")
                logger.info(f"Using LiteLLM fast LLM: {os.getenv('LITELLM_FAST_LLM')}")
            if os.getenv("LITELLM_SMART_LLM"):
                os.environ["SMART_LLM"] = os.getenv("LITELLM_SMART_LLM")
                logger.info(f"Using LiteLLM smart LLM: {os.getenv('LITELLM_SMART_LLM')}")
            if os.getenv("LITELLM_STRATEGIC_LLM"):
                os.environ["STRATEGIC_LLM"] = os.getenv("LITELLM_STRATEGIC_LLM")
                logger.info(f"Using LiteLLM strategic LLM: {os.getenv('LITELLM_STRATEGIC_LLM')}")

        # Embedding selection: prefer explicit user selection, then env vars, then smart defaults
        if litellm_embedding_model:
            # User explicitly selected an embedding model from the dropdown
            os.environ["EMBEDDING"] = _with_provider_prefix("openai", litellm_embedding_model)
            logger.info(f"Using LiteLLM embedding model (user selected): {os.environ.get('EMBEDDING')}")
        elif litellm_model and "embedding" in litellm_model:
            # User selected LLM happens to be an embedding model
            os.environ["EMBEDDING"] = _with_provider_prefix("openai", litellm_model)
            logger.info(f"Using LiteLLM embedding (from LLM model): {os.environ.get('EMBEDDING')}")
        elif os.getenv("LITELLM_EMBEDDING"):
            # Fall back to environment variable
            os.environ["EMBEDDING"] = os.getenv("LITELLM_EMBEDDING")
            logger.info(f"Using LiteLLM embedding (from env): {os.getenv('LITELLM_EMBEDDING')}")
        elif not os.getenv("EMBEDDING"):
            # Final fallback to a sane default
            os.environ["EMBEDDING"] = "openai:text-embedding-3-large"
            logger.info(f"Defaulting embedding to: {os.environ.get('EMBEDDING')}")
    
    else:
        logger.warning(f"Unknown LLM provider mode: {llm_provider_mode}. Using default configuration.")


class CustomLogsHandler:
    """Custom handler to capture streaming logs from the research process"""
    def __init__(self, websocket, task: str):
        self.logs = []
        self.websocket = websocket
        sanitized_filename = sanitize_filename(f"task_{int(time.time())}_{task}")
        self.log_file = os.path.join("outputs", f"{sanitized_filename}.json")
        self.timestamp = datetime.now().isoformat()
        # Initialize log file with metadata
        os.makedirs("outputs", exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump({
                "timestamp": self.timestamp,
                "events": [],
                "content": {
                    "query": "",
                    "sources": [],
                    "context": [],
                    "report": "",
                    "costs": 0.0
                }
            }, f, indent=2)

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Store log data and send to websocket"""
        # Send to websocket for real-time display
        if self.websocket:
            await self.websocket.send_json(data)
            
        # Read current log file
        with open(self.log_file, 'r') as f:
            log_data = json.load(f)
            
        # Update appropriate section based on data type
        if data.get('type') == 'logs':
            log_data['events'].append({
                "timestamp": datetime.now().isoformat(),
                "type": "event",
                "data": data
            })
        else:
            # Update content section for other types of data
            log_data['content'].update(data)
            
        # Save updated log file
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)


class Researcher:
    def __init__(self, query: str, report_type: str = "research_report"):
        self.query = query
        self.report_type = report_type
        # Generate unique ID for this research task
        self.research_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(query)}"
        # Initialize logs handler with research ID
        self.logs_handler = CustomLogsHandler(None, self.research_id)
        self.researcher = GPTResearcher(
            query=query,
            report_type=report_type,
            websocket=self.logs_handler
        )

    async def research(self) -> dict:
        """Conduct research and return paths to generated files"""
        await self.researcher.conduct_research()
        report = await self.researcher.write_report()
        
        # Generate the files
        sanitized_filename = sanitize_filename(f"task_{int(time.time())}_{self.query}")
        file_paths = await generate_report_files(report, sanitized_filename)
        
        # Get the JSON log path that was created by CustomLogsHandler
        json_relative_path = os.path.relpath(self.logs_handler.log_file)
        
        return {
            "output": {
                **file_paths,  # Include PDF, DOCX, and MD paths
                "json": json_relative_path
            }
        }

def sanitize_filename(filename: str) -> str:
    # Split into components
    prefix, timestamp, *task_parts = filename.split('_')
    task = '_'.join(task_parts)
    
    # Calculate max length for task portion
    # 255 - len(os.getcwd()) - len("\\gpt-researcher\\outputs\\") - len("task_") - len(timestamp) - len("_.json") - safety_margin
    max_task_length = 255 - len(os.getcwd()) - 24 - 5 - 10 - 6 - 5  # ~189 chars for task
    
    # Truncate task if needed
    truncated_task = task[:max_task_length] if len(task) > max_task_length else task
    
    # Reassemble and clean the filename
    sanitized = f"{prefix}_{timestamp}_{truncated_task}"
    return re.sub(r"[^\w\s-]", "", sanitized).strip()


async def handle_start_command(websocket, data: str, manager):
    json_data = json.loads(data[6:])
    (
        task,
        report_type,
        source_urls,
        document_urls,
        tone,
        headers,
        report_source,
        query_domains,
        mcp_enabled,
        mcp_strategy,
        mcp_configs,
        llm_provider_mode,
        ollama_base_url,
        ollama_model,
        ollama_embedding_model,
        litellm_base_url,
        litellm_api_key,
        litellm_model,
        litellm_embedding_model,
    ) = extract_command_data(json_data)

    if not task or not report_type:
        print("Error: Missing task or report_type")
        return

    # Apply LLM provider mode environment overrides :-)
    apply_llm_provider_mode(
        llm_provider_mode,
        ollama_base_url,
        ollama_model,
        ollama_embedding_model,
        litellm_base_url,
        litellm_api_key,
        litellm_model,
        litellm_embedding_model,
    )

    # Create logs handler with websocket and task
    logs_handler = CustomLogsHandler(websocket, task)
    # Initialize log content with query
    await logs_handler.send_json({
        "query": task,
        "sources": [],
        "context": [],
        "report": ""
    })

    sanitized_filename = sanitize_filename(f"task_{int(time.time())}_{task}")

    report = await manager.start_streaming(
        task,
        report_type,
        report_source,
        source_urls,
        document_urls,
        tone,
        websocket,
        headers,
        query_domains,
        mcp_enabled,
        mcp_strategy,
        mcp_configs,
    )
    report = str(report)
    file_paths = await generate_report_files(report, sanitized_filename)
    # Add JSON log path to file_paths
    file_paths["json"] = os.path.relpath(logs_handler.log_file)
    await send_file_paths(websocket, file_paths)


async def handle_chat_command(websocket, data: str):
    """Handle chat command from WebSocket"""
    try:
        # Parse chat data (format: "chat {json_data}")
        chat_data = json.loads(data[5:])  # Skip "chat " prefix
        
        message = chat_data.get("message", "")
        report = chat_data.get("report", "")
        messages = chat_data.get("messages", [])
        
        # Debug logging
        logger.info(f"Chat data keys: {list(chat_data.keys())}")
        logger.info(f"Report length: {len(report) if report else 0} characters")
        logger.info(f"Report preview: {report[:100] if report else '(empty)'}")
        
        if not message and not messages:
            await websocket.send_json({
                "type": "error",
                "content": "No message provided"
            })
            return
        
        # Warn if no report provided
        if not report:
            logger.warning("⚠️ No report provided in chat request! AI won't have context.")
        
        logger.info(f"Processing chat with message: {message[:50]}...")
        
        # Import chat agent here to avoid circular imports
        from backend.chat.chat import ChatAgentWithMemory
        
        # Create chat agent with the report
        chat_agent = ChatAgentWithMemory(
            report=report,
            config_path="default",
            headers=None
        )
        
        # If we have a single message, append it to messages list
        if message and not messages:
            messages = [{"role": "user", "content": message}]
        elif message:
            messages.append({"role": "user", "content": message})
        
        # Process the chat and get response with metadata
        response_content, tool_calls_metadata = await chat_agent.chat(messages, websocket)
        
        logger.info(f"Got chat response of length: {len(response_content) if response_content else 0}")
        
        # Send response back through websocket
        response_message = {
            "type": "chat",
            "content": response_content,
            "metadata": {
                "tool_calls": tool_calls_metadata
            } if tool_calls_metadata else None
        }
        
        await websocket.send_json(response_message)
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse chat data: {e}")
        await websocket.send_json({
            "type": "error",
            "content": f"Invalid JSON in chat command: {str(e)}"
        })
    except Exception as e:
        logger.error(f"Error processing chat command: {str(e)}", exc_info=True)
        await websocket.send_json({
            "type": "error",
            "content": f"Error processing chat: {str(e)}"
        })

async def handle_human_feedback(data: str):
    feedback_data = json.loads(data[14:])  # Remove "human_feedback" prefix
    print(f"Received human feedback: {feedback_data}")
    # TODO: Add logic to forward the feedback to the appropriate agent or update the research state

async def generate_report_files(report: str, filename: str) -> Dict[str, str]:
    pdf_path = await write_md_to_pdf(report, filename)
    docx_path = await write_md_to_word(report, filename)
    md_path = await write_text_to_md(report, filename)
    return {"pdf": pdf_path, "docx": docx_path, "md": md_path}


async def send_file_paths(websocket, file_paths: Dict[str, str]):
    await websocket.send_json({"type": "path", "output": file_paths})


def get_config_dict(
    langchain_api_key: str, openai_api_key: str, firecrawl_api_key: str,
    google_api_key: str, google_cx_key: str, bing_api_key: str,
    searchapi_api_key: str, serpapi_api_key: str, serper_api_key: str, searx_url: str
) -> Dict[str, str]:
    return {
        "LANGCHAIN_API_KEY": langchain_api_key or os.getenv("LANGCHAIN_API_KEY", ""),
        "OPENAI_API_KEY": openai_api_key or os.getenv("OPENAI_API_KEY", ""),
        "FIRECRAWL_API_KEY": firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY", ""),
        "GOOGLE_API_KEY": google_api_key or os.getenv("GOOGLE_API_KEY", ""),
        "GOOGLE_CX_KEY": google_cx_key or os.getenv("GOOGLE_CX_KEY", ""),
        "BING_API_KEY": bing_api_key or os.getenv("BING_API_KEY", ""),
        "SEARCHAPI_API_KEY": searchapi_api_key or os.getenv("SEARCHAPI_API_KEY", ""),
        "SERPAPI_API_KEY": serpapi_api_key or os.getenv("SERPAPI_API_KEY", ""),
        "SERPER_API_KEY": serper_api_key or os.getenv("SERPER_API_KEY", ""),
        "SEARX_URL": searx_url or os.getenv("SEARX_URL", ""),
        "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2", "true"),
        "DOC_PATH": os.getenv("DOC_PATH", "./my-docs"),
        "RETRIEVER": os.getenv("RETRIEVER", ""),
        "EMBEDDING_MODEL": os.getenv("OPENAI_EMBEDDING_MODEL", "")
    }


def update_environment_variables(config: Dict[str, str]):
    for key, value in config.items():
        os.environ[key] = value


async def handle_file_upload(file, DOC_PATH: str) -> Dict[str, str]:
    file_path = os.path.join(DOC_PATH, os.path.basename(file.filename))
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"File uploaded to {file_path}")

    document_loader = DocumentLoader(DOC_PATH)
    await document_loader.load()

    return {"filename": file.filename, "path": file_path}


async def handle_file_deletion(filename: str, DOC_PATH: str) -> JSONResponse:
    file_path = os.path.join(DOC_PATH, os.path.basename(filename))
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File deleted: {file_path}")
        return JSONResponse(content={"message": "File deleted successfully"})
    else:
        print(f"File not found: {file_path}")
        return JSONResponse(status_code=404, content={"message": "File not found"})


async def execute_multi_agents(manager) -> Any:
    websocket = manager.active_connections[0] if manager.active_connections else None
    if websocket:
        report = await run_research_task("Is AI in a hype cycle?", websocket, stream_output)
        return {"report": report}
    else:
        return JSONResponse(status_code=400, content={"message": "No active WebSocket connection"})


async def handle_websocket_communication(websocket, manager):
    running_task: asyncio.Task | None = None

    def run_long_running_task(awaitable: Awaitable) -> asyncio.Task:
        async def safe_run():
            try:
                await awaitable
            except asyncio.CancelledError:
                logger.info("Task cancelled.")
                raise
            except Exception as e:
                logger.error(f"Error running task: {e}\n{traceback.format_exc()}")
                await websocket.send_json(
                    {
                        "type": "logs",
                        "content": "error",
                        "output": f"Error: {e}",
                    }
                )

        return asyncio.create_task(safe_run())

    try:
        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message: {data[:50]}..." if len(data) > 50 else data)
                
                if data == "ping":
                    await websocket.send_text("pong")
                elif running_task and not running_task.done():
                    # discard any new request if a task is already running
                    logger.warning(
                        f"Received request while task is already running. Request data preview: {data[: min(20, len(data))]}..."
                    )
                    await websocket.send_json(
                        {
                            "type": "logs",
                            "content": "warning",
                            "output": "Task already running. Please wait.",
                        }
                    )
                # Normalize command detection by checking startswith after stripping whitespace
                elif data.strip().startswith("start"):
                    logger.info(f"Processing start command")
                    running_task = run_long_running_task(
                        handle_start_command(websocket, data, manager)
                    )
                elif data.strip().startswith("human_feedback"):
                    logger.info(f"Processing human_feedback command")
                    running_task = run_long_running_task(handle_human_feedback(data))
                elif data.strip().startswith("chat"):
                    logger.info(f"Processing chat command")
                    running_task = run_long_running_task(handle_chat_command(websocket, data))
                else:
                    error_msg = f"Error: Unknown command or not enough parameters provided. Received: '{data[:100]}...'" if len(data) > 100 else f"Error: Unknown command or not enough parameters provided. Received: '{data}'"
                    logger.error(error_msg)
                    print(error_msg)
                    await websocket.send_json({
                        "type": "error",
                        "content": "error",
                        "output": "Unknown command received by server"
                    })
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}\n{traceback.format_exc()}")
                print(f"WebSocket error: {e}")
                break
    finally:
        if running_task and not running_task.done():
            running_task.cancel()

def extract_command_data(json_data: Dict) -> tuple:
    return (
        json_data.get("task"),
        json_data.get("report_type"),
        json_data.get("source_urls"),
        json_data.get("document_urls"),
        json_data.get("tone"),
        json_data.get("headers", {}),
        json_data.get("report_source"),
        json_data.get("query_domains", []),
        json_data.get("mcp_enabled", False),
        json_data.get("mcp_strategy", "fast"),
        json_data.get("mcp_configs", []),
        json_data.get("llm_provider_mode", "litellm"),
        json_data.get("ollama_base_url"),
        json_data.get("ollama_model"),
        json_data.get("ollama_embedding_model"),
        json_data.get("litellm_base_url"),
        json_data.get("litellm_api_key"),
        json_data.get("litellm_model"),
        json_data.get("litellm_embedding_model"),
    )
