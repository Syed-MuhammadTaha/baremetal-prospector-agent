from .registry import tool

@tool
def save_dossier(company_name: str, content: str) -> str:
    """Save the final finalized target research and cold email template to a local markdown file."""
    try:
        filename = f"{company_name.lower().replace(' ', '_')}_prospect.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Success: Dossier written safely to {filename}"
    except Exception as e:
        return f"File writing error: {str(e)}"