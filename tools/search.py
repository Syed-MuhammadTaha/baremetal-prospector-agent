from .registry import tool
from tavily import TavilyClient
from config import TAVILY_API_KEY

@tool
def search(query: str) -> str:
    """Searches using tavily api for information."""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    try: 
        response = client.search(query)
        formatted_results = []
        for r in response['results'][:3]: # Limit to top 3 results for context space
            
            # --- COMPRESSION FIX ---
            snippet = r.get('content', '')
            if len(snippet) > 4000:
                snippet = f"{snippet[:2500]}\n\n[... OMITTED MIDDLE CONTENTS FOR BREVITY ...]\n\n{snippet[-1500:]}"
            # -----------------------
            
            formatted_results.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {snippet}\n---")
        return "\n".join(formatted_results) if formatted_results else "No results found."
    except Exception as e:
        raise Exception(f"Search error: {str(e)}")