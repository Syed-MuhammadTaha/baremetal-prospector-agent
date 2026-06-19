import inspect
from functools import wraps
from typing import Callable, Any, Dict, Optional

TOOL_REGISTRY: Dict[str, "CustomTool"] = {}


class CustomTool:
    """A wrapper class that bundles the execution logic and LLM schema together."""
    def __init__(self, func: Callable[..., Any], name: Optional[str] = None, description: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__
        # Fallback to the docstring if no custom description is provided
        self.description = description or (func.__doc__ or "").strip()
        self.schema = self._generate_schema()

    def _generate_schema(self) -> Dict[str, Any]:
        """Extracts type hints to create a JSON-schema-like dictionary for LLMs."""
        sig = inspect.signature(self.func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            # Extract basic type string representation from type hints
            type_name = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else "any"
            parameters[param_name] = {
                "type": type_name,
                "required": param.default == inspect.Parameter.empty
            }
            
        return {
            "name": self.name,
            "description": self.description,
            "parameters": parameters
        }

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Executes the underlying tool function when called."""
        return self.func(*args, **kwargs)


def tool(_func: Optional[Callable[..., Any]] = None, *, name: Optional[str] = None, description: Optional[str] = None) -> Any:
    """The actual decorator function managing both positional and keyword parameters."""
    def decorator(func: Callable[..., Any]) -> CustomTool:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        custom_tool = CustomTool(func, name=name, description=description)
        TOOL_REGISTRY[custom_tool.name] = custom_tool
        return custom_tool

    # Handles the case where the decorator is called without parentheses: @tool
    if _func is not None:
        return decorator(_func)
    
    # Handles the case where the decorator is called with parameters: @tool(name="...")
    return decorator
