from pydoc import text
from bs4 import BeautifulSoup
import requests
from .registry import tool

@tool
def scrape(url: str) -> str:
    """Scrapes a website for information."""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)
        
        # Managing context by using initial and final characters based on recommnedation from AI engineer youtube channel
        if len(clean_text) > 4000:
            return f"{clean_text[:2500]}\n\n[... OMITTED MIDDLE CONTENTS FOR BREVITY ...]\n\n{clean_text[-1500:]}"
        return clean_text
    except Exception as e:
        return f"Scraping error: {str(e)}"