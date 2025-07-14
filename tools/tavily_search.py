from langchain_community.tools.tavily_search import TavilySearchResults

tavily_api_key = "YOUR-API_KEY"

# Initialize the Tavily
# from langchain_community.tools.tavily_search import TavilySearchResults
tavily_tool = TavilySearchResults(tavily_api_key=tavily_api_key, max_results=3)