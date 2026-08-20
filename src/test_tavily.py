import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()   

client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

response = client.search(
    query="latest news about Anthropic",
    search_depth="basic",
    max_results=3
)

for result in response["results"]:
    print(result["title"])
    print(result["url"])
    print(result["content"][:200])
    print("---")
