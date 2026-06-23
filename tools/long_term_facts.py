import os
import json
from .registry import tool
from config import KNOWLEDGE_FILE

@tool
def update_company_knowledge(category: str, fact: str) -> str:
    """
    CRITICAL: ONLY use this tool to save permanent facts about OUR company (Sable).
    This acts as a key-value patch. 
    Examples of category: "pricing", "deployment", "target_audience".
    Examples of fact: "Minimum project size is $15k", "We are cloud-only."
    """
    if not os.path.exists(KNOWLEDGE_FILE):
        return "Error: sable_knowledge.json core file is missing."

    with open(KNOWLEDGE_FILE, "r") as f:
        knowledge_base = json.load(f)

    # Apply the patch to the dictionary
    knowledge_base["patches"][category] = fact
    
    with open(KNOWLEDGE_FILE, "w") as f:
        json.dump(knowledge_base, f, indent=4)
        
    return f"Success: Patched memory category '[{category}]' with -> '{fact}'"