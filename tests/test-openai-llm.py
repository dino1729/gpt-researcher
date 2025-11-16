import asyncio
import os
from gpt_researcher.utils.llm import get_llm
from gpt_researcher import GPTResearcher
from dotenv import load_dotenv
load_dotenv()

async def main():

    # Example usage of get_llm function - model must be set in .env file
    llm_provider = "openai"
    model = os.getenv("FAST_LLM", "openai:gpt-4o-mini").split(":")[-1]  # Get model from env, default to gpt-4o-mini
    temperature = 0.7
    max_tokens = 1000

    llm = get_llm(llm_provider, model=model, temperature=temperature, max_tokens=max_tokens)
    print(f"LLM Provider: {llm_provider}, Model: {model}, Temperature: {temperature}, Max Tokens: {max_tokens}")
    print('llm: ',llm)
    await test_llm(llm=llm)


async def test_llm(llm):
    # Test the connection with a simple query
    messages = [{"role": "user", "content": "sup?"}]
    try:
        response = await llm.get_chat_response(messages, stream=False)
        print("LLM response:", response)
    except Exception as e:
        print(f"Error: {e}")

# Run the async function
asyncio.run(main())
