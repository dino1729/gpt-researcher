import logging
import os
import uuid
import json
from fastapi import WebSocket
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load .env file and override system environment variables
load_dotenv(override=True)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import InMemoryVectorStore
from gpt_researcher.memory import Memory
from gpt_researcher.config.config import Config
from gpt_researcher.utils.llm import create_chat_completion
from datetime import datetime

# Setup logging
# Get logger instance
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Only log to console
    ]
)

# Note: LLM client is now handled through GPT Researcher's unified LLM system
# This supports all configured providers (OpenAI, Google Gemini, Anthropic, etc.)

class ChatAgentWithMemory:
    def __init__(
        self,
        report: str,
        config_path="default",
        headers=None,
        vector_store=None
    ):
        self.report = report
        self.headers = headers
        self.config = Config(config_path)
        self.vector_store = vector_store
        self.retriever = None

        # Process document and create vector store if not provided
        if not self.vector_store and False:
            self._setup_vector_store()

    def _setup_vector_store(self):
        """Setup vector store for document retrieval"""
        # Process document into chunks
        documents = self._process_document(self.report)

        # Create unique thread ID
        self.thread_id = str(uuid.uuid4())

        # Setup embeddings and vector store
        cfg = Config()
        self.embedding = Memory(
            cfg.embedding_provider,
            cfg.embedding_model,
            **cfg.embedding_kwargs
        ).get_embeddings()

        # Create vector store and retriever
        self.vector_store = InMemoryVectorStore(self.embedding)
        self.vector_store.add_texts(documents)
        self.retriever = self.vector_store.as_retriever(k=4)

    def _process_document(self, report):
        """Split Report into Chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        documents = text_splitter.split_text(report)
        return documents

    async def chat(self, messages, websocket=None):
        """Chat with configured LLM provider (supports OpenAI, Google Gemini, Anthropic, etc.)

        Args:
            messages: List of chat messages with role and content
            websocket: Optional websocket for streaming responses

        Returns:
            tuple: (str: The AI response message, dict: empty metadata dict)
        """
        try:
            # Format system prompt with the report context
            system_prompt = f"""
            You are GPT Researcher, an autonomous research agent created by an open source community at https://github.com/assafelovic/gpt-researcher, homepage: https://gptr.dev.
            To learn more about GPT Researcher you can suggest to check out: https://docs.gptr.dev.

            This is a chat about a research report that you created. Answer based on the given context and report.
            You must include citations to your answer based on the report.

            Answer based only on the report content provided. If the user asks about current events or information
            not in the report, politely explain that you can only answer based on the report content and suggest
            they run a new research query for updated information.

            You must respond in markdown format. You must make it readable with paragraphs, tables, etc when possible.
            Remember that you're answering in a chat not a report.

            Assume the current time is: {datetime.now()}.

            Report: {self.report}

            """

            # Format message history
            formatted_messages = []

            # Add system message first
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })

            # Add user/assistant message history - filter out non-essential fields
            for msg in messages:
                if 'role' in msg and 'content' in msg:
                    formatted_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                else:
                    logger.warning(f"Skipping message with missing role or content: {msg}")

            # Process the chat using configured LLM provider
            ai_message = await create_chat_completion(
                messages=formatted_messages,
                model=self.config.smart_llm_model,
                llm_provider=self.config.smart_llm_provider,
                llm_kwargs=self.config.llm_kwargs,
            )

            # Provide fallback response if message is empty
            if not ai_message:
                logger.warning("No AI message content found in response, using fallback message")
                ai_message = "I apologize, but I couldn't generate a proper response. Please try asking your question again."

            logger.info(f"Generated response: {ai_message[:100]}..." if len(ai_message) > 100 else f"Generated response: {ai_message}")

            # Return both the message and empty metadata (no tool usage)
            return ai_message, []

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}", exc_info=True)
            raise

    def get_context(self):
        """return the current context of the chat"""
        return self.report
