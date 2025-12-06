import os
from typing import Any

OPENAI_EMBEDDING_MODEL = os.environ.get(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)

_SUPPORTED_PROVIDERS = {
    "openai",
    "azure_openai",
    "cohere",
    "gigachat",
    "google_vertexai",
    "google_genai",
    "fireworks",
    "ollama",
    "together",
    "mistralai",
    "huggingface",
    "nomic",
    "voyageai",
    "dashscope",
    "custom",
    "bedrock",
    "aimlapi",
    "netmind",
}


class NVIDIAOpenAIEmbeddings:
    """Custom wrapper for NVIDIA asymmetric embedding models that require input_type parameter.

    NVIDIA's asymmetric models like llama-3.2-nv-embedqa-1b-v2 require an input_type parameter:
    - "passage" for documents being indexed
    - "query" for search queries

    This wrapper ensures the correct input_type is passed via extra_body for each operation.
    """

    def __init__(self, **kwargs):
        from langchain_openai import OpenAIEmbeddings
        self._embeddings = OpenAIEmbeddings(**kwargs)

    def embed_documents(self, texts: list[str], chunk_size: int | None = None) -> list[list[float]]:
        """Embed documents with input_type='passage' in extra_body."""
        # Monkey-patch the client to inject extra_body
        original_create = self._embeddings.client.create

        def create_with_input_type(**kwargs):
            # Add input_type to extra_body
            if 'extra_body' not in kwargs:
                kwargs['extra_body'] = {}
            kwargs['extra_body']['input_type'] = 'passage'
            return original_create(**kwargs)

        self._embeddings.client.create = create_with_input_type
        try:
            result = self._embeddings.embed_documents(texts, chunk_size)
        finally:
            # Restore original method
            self._embeddings.client.create = original_create

        return result

    def embed_query(self, text: str) -> list[float]:
        """Embed a query with input_type='query' in extra_body."""
        # Monkey-patch the client to inject extra_body
        original_create = self._embeddings.client.create

        def create_with_input_type(**kwargs):
            # Add input_type to extra_body
            if 'extra_body' not in kwargs:
                kwargs['extra_body'] = {}
            kwargs['extra_body']['input_type'] = 'query'
            return original_create(**kwargs)

        self._embeddings.client.create = create_with_input_type
        try:
            result = self._embeddings.embed_query(text)
        finally:
            # Restore original method
            self._embeddings.client.create = original_create

        return result

    def __getattr__(self, name):
        """Delegate all other attributes to the underlying embeddings object."""
        return getattr(self._embeddings, name)


class Memory:
    def __init__(self, embedding_provider: str, model: str, **embedding_kwargs: Any):
        _embeddings = None
        match embedding_provider:
            case "custom":
                from langchain_openai import OpenAIEmbeddings

                _embeddings = OpenAIEmbeddings(
                    model=model,
                    openai_api_key=os.getenv("OPENAI_API_KEY", "custom"),
                    openai_api_base=os.getenv(
                        "OPENAI_BASE_URL", "http://localhost:1234/v1"
                    ),  # default for lmstudio
                    check_embedding_ctx_length=False,
                    **embedding_kwargs,
                )  # quick fix for lmstudio
            case "openai":
                # Support custom OpenAI-compatible APIs via OPENAI_BASE_URL
                if "openai_api_base" not in embedding_kwargs and os.environ.get("OPENAI_BASE_URL"):
                    embedding_kwargs["openai_api_base"] = os.environ["OPENAI_BASE_URL"]

                # For NVIDIA embedding models, use custom wrapper that handles input_type
                if "nv-embedqa" in model or "llama-3.2-nv-embedqa" in model:
                    # Initialize model_kwargs if not present
                    if "model_kwargs" not in embedding_kwargs:
                        embedding_kwargs["model_kwargs"] = {}

                    # Set check_embedding_ctx_length to False to avoid issues
                    embedding_kwargs["check_embedding_ctx_length"] = False

                    # Use custom wrapper that sets input_type appropriately
                    _embeddings = NVIDIAOpenAIEmbeddings(model=model, **embedding_kwargs)
                else:
                    from langchain_openai import OpenAIEmbeddings
                    _embeddings = OpenAIEmbeddings(model=model, **embedding_kwargs)
            case "azure_openai":
                from langchain_openai import AzureOpenAIEmbeddings

                _embeddings = AzureOpenAIEmbeddings(
                    model=model,
                    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                    openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
                    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
                    **embedding_kwargs,
                )
            case "cohere":
                from langchain_cohere import CohereEmbeddings

                _embeddings = CohereEmbeddings(model=model, **embedding_kwargs)
            case "google_vertexai":
                from langchain_google_vertexai import VertexAIEmbeddings

                _embeddings = VertexAIEmbeddings(model=model, **embedding_kwargs)
            case "google_genai":
                from langchain_google_genai import GoogleGenerativeAIEmbeddings

                _embeddings = GoogleGenerativeAIEmbeddings(
                    model=model, **embedding_kwargs
                )
            case "fireworks":
                from langchain_fireworks import FireworksEmbeddings

                _embeddings = FireworksEmbeddings(model=model, **embedding_kwargs)
            case "gigachat":
                from langchain_gigachat import GigaChatEmbeddings

                _embeddings = GigaChatEmbeddings(model=model, **embedding_kwargs)
            case "ollama":
                from langchain_ollama import OllamaEmbeddings

                _embeddings = OllamaEmbeddings(
                    model=model,
                    base_url=os.environ["OLLAMA_BASE_URL"],
                    **embedding_kwargs,
                )
            case "together":
                from langchain_together import TogetherEmbeddings

                _embeddings = TogetherEmbeddings(model=model, **embedding_kwargs)
            case "netmind":
                from langchain_netmind import NetmindEmbeddings

                _embeddings = NetmindEmbeddings(model=model, **embedding_kwargs)
            case "mistralai":
                from langchain_mistralai import MistralAIEmbeddings

                _embeddings = MistralAIEmbeddings(model=model, **embedding_kwargs)
            case "huggingface":
                from langchain_huggingface import HuggingFaceEmbeddings

                _embeddings = HuggingFaceEmbeddings(model_name=model, **embedding_kwargs)
            case "nomic":
                from langchain_nomic import NomicEmbeddings

                _embeddings = NomicEmbeddings(model=model, **embedding_kwargs)
            case "voyageai":
                from langchain_voyageai import VoyageAIEmbeddings

                _embeddings = VoyageAIEmbeddings(
                    voyage_api_key=os.environ["VOYAGE_API_KEY"],
                    model=model,
                    **embedding_kwargs,
                )
            case "dashscope":
                from langchain_community.embeddings import DashScopeEmbeddings

                _embeddings = DashScopeEmbeddings(model=model, **embedding_kwargs)
            case "bedrock":
                from langchain_aws.embeddings import BedrockEmbeddings

                _embeddings = BedrockEmbeddings(model_id=model, **embedding_kwargs)
            case "aimlapi":
                from langchain_openai import OpenAIEmbeddings

                _embeddings = OpenAIEmbeddings(
                    model=model,
                    openai_api_key=os.getenv("AIMLAPI_API_KEY"),
                    openai_api_base=os.getenv("AIMLAPI_BASE_URL", "https://api.aimlapi.com/v1"),
                    **embedding_kwargs,
                )
            case _:
                raise Exception("Embedding not found.")

        self._embeddings = _embeddings

    def get_embeddings(self):
        return self._embeddings
