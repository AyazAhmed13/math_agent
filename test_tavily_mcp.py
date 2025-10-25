'''import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse, parse_qs

load_dotenv()

MCP_SEARCH_ARGS = os.getenv("MCP_SEARCH_ARGS")

# Extract API key from the MCP URL
parsed = urlparse(MCP_SEARCH_ARGS)
API_KEY = parse_qs(parsed.query).get("tavilyApiKey", [None])[0]

query = "What is the derivative of sin(x)?"
print(f"🔍 Testing Tavily MCP connection with query: {query}")

url = "https://api.tavily.com/search"
headers = {"Authorization": f"Bearer {API_KEY}"}
payload = {
    "query": query,
    "include_answer": True,   # <-- Force Tavily to include AI-generated summary
    "max_results": 5
}

response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()

data = response.json()

print("\n✅ Connection Successful!")
print("Result Summary:")
print(data.get("answer", "No AI-generated summary available"))
print("\nSources:")
for src in data.get("results", []):
    print("-", src.get("url"))
'''

import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("TAVILY_API_KEY")

if not API_KEY:
    raise ValueError("No Tavily API key found in .env")

query = "What is the derivative of sin(x)?"
print(f"🔍 Testing Tavily REST API with query: {query}")

url = "https://api.tavily.com/search"
headers = {"Authorization": f"Bearer {API_KEY}"}
payload = {"query": query, "include_answer": True, "max_results": 5}

response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()
data = response.json()

print("\n✅ Connection Successful!")
print("Result Summary:")
print(data.get("answer", "No AI-generated summary available"))
print("\nSources:")
for src in data.get("results", []):
    print("-", src.get("url"))
