from .registry import tool
from agent.vectorstore import save_semantic_memory, search_semantic_memory

@tool
def save_lesson(lesson: str) -> str:
    """
    Saves a small lesson, heuristic, or user preference into semantic memory.
    Use this to record nuances about how to write emails, handle specific industries, 
    or what the human operator likes.
    Example: "The human prefers aggressive subject lines."
    """
    try:
        save_semantic_memory(lesson)
        return f"Success: Embedded and saved lesson to semantic memory -> '{lesson}'"
    except Exception as e:
        return f"Error saving semantic memory: {str(e)}"

@tool
def recall_knowledge(query: str) -> str:
    """
    Searches semantic memory for past lessons, heuristics, or case studies.
    Use this BEFORE drafting an email or making a strategy decision to see if you 
    already have relevant preferences or industry playbooks saved.
    Example: "How should I write emails for healthcare?" or "Sales copy preferences"
    """
    try:
        results = search_semantic_memory(query, top_k=3)
        if not results:
            return "No relevant past lessons or heuristics found for this query."
            
        formatted_results = "\n- ".join(results)
        return f"Found relevant internal knowledge/lessons:\n- {formatted_results}"
    except Exception as e:
        return f"Error searching semantic memory: {str(e)}"