import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def search_web(question: str) -> str:
    """
Receives the user's question, returns a single text compiled from the search results, ready to be used as context for the LLM later..
    """
    response = tavily_client.search(
        query=question,
        search_depth="basic",
        max_results=3
    )

    if not response["results"]:
        return None  

    combined = ""
    for result in response["results"]:
        combined += f"Source: {result['url']}\n{result['content']}\n\n"

    return combined.strip()


if __name__ == "__main__":
    test_question = "What is the latest news about Anthropic?"
    result = search_web(test_question)
    print(result)
