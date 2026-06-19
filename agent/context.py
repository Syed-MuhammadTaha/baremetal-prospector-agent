from .prompt import BASE_SYSTEM_PROMPT
import tools 
from tools.registry import TOOL_REGISTRY
from importlib import resources
import json

def get_value_prop() -> str:
    """Reads the long-term memory (your startup pitch) from the .txt file."""
    try:
        value_prop = resources.read_text("agent", "value_prop.txt")
        return value_prop
    except Exception as e:
        return "[WARNING: value_prop.txt not found. Proceeding with generic AI automation sales pitch.]"

def get_tools_string() -> str:
    """Constructs a string of all available tools for the LLM to reference."""
    try:
        if not TOOL_REGISTRY:
            raise Exception("TOOL_REGISTRY is empty — tool modules were not imported.")

        return "\n".join(
            f"{tool.name}: {tool.description}\n{json.dumps(tool.schema['parameters'], indent=2)}"
            for tool in TOOL_REGISTRY.values()
        )
    except Exception as e:
        raise Exception(f"Error constructing tools string: {str(e)}")

def get_system_prompt() -> str:
    """Gets the system prompt with the value prop and tools string."""
    try:
        return BASE_SYSTEM_PROMPT.format(value_prop=get_value_prop(), tools_string=get_tools_string())
    except Exception as e:
        raise Exception(f"Error getting system prompt: {str(e)}")