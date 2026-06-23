from .prompt import BASE_SYSTEM_PROMPT
from tools.registry import TOOL_REGISTRY
import json
import os

KNOWLEDGE_FILE = "sable_knowledge.json"

def get_canonical_memory() -> str:
    """Reads the JSON OS and formats it as a base + diff patches."""
    if not os.path.exists(KNOWLEDGE_FILE):
        return "[WARNING: sable_knowledge.json not found. Proceeding blind.]"

    try:
        with open(KNOWLEDGE_FILE, "r") as f:
            db = json.load(f)
            
        base = db.get("base_pitch", "")
        patches = db.get("patches", {})
        
        # Build the Diff-Style Injection
        memory_string = f"--- CORE IDENTITY ---\n{base}\n\n"
        
        if patches:
            memory_string += "--- RECENT KNOWLEDGE PATCHES (These override core assumptions) ---\n"
            for key, val in patches.items():
                memory_string += f"+ [{key.upper()}]: {val}\n"
                
        return memory_string
        
    except Exception as e:
        return f"[MEMORY CORRUPTION ERROR: {str(e)}]"

def get_tools_string() -> str:
    """Constructs a string of all available tools for the LLM to reference."""
    if not TOOL_REGISTRY:
        raise Exception("TOOL_REGISTRY is empty — tool modules were not imported.")

    return "\n".join(
        f"{tool.name}: {tool.description}\n{json.dumps(tool.schema['parameters'], indent=2)}"
        for tool in TOOL_REGISTRY.values()
    )

def get_system_prompt() -> str:
    """Gets the system prompt with the canonical memory and tools string."""
    return BASE_SYSTEM_PROMPT.format(
        value_prop=get_canonical_memory(), 
        tools_string=get_tools_string()
    )