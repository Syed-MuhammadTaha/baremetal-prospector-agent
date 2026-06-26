from .context import get_system_prompt
import tools  # noqa: F401 — ensure tools are registered for execution
from tools.registry import TOOL_REGISTRY
from .parser import parse_llm_output
from .llm import agent_llm
from .memory import ShortTermManager

def run_agent(query: str, chat_history: list = None, max_steps: int = 10):
    """The core execution engine of the autonomous agent."""
    print(f"\n🚀 INITIALIZING AGENT FOR: {query}")
    
    # 1. Assemble the rules and tools
    system_prompt = get_system_prompt()

    print("System prompt loaded.")
    print("-" * 40)
    
    # 2. Initialize Working Memory (The State)
    if chat_history is None:
        # First turn: Create a fresh message array
        messages = [
            {"role": "system", "content": system_prompt}
        ]
    else:
        # Subsequent turns: Load the history
        messages = chat_history
        # CRITICAL: Always refresh the system prompt! 
        # If the human updated the Tier 3 JSON memory in the last turn, 
        # this ensures the agent reads the new patches.
        messages[0]["content"] = system_prompt
        
    # Append the user's newest command
    messages.append({"role": "user", "content": query})

    print("✅ Context Assembled. State Initialized.")
    print("-" * 40)

    memory_manager = ShortTermManager(max_tail=6, chunk_size=4)
    
    # --- METRICS TRACKING ---
    metrics = {
        "iterations": 0,
        "tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "queue_time": 0.0,
        "prompt_time": 0.0,
        "completion_time": 0.0,
        "total_time": 0.0
    }
    # ------------------------

    for step in range(max_steps):
        iterations = step + 1
        print(f"\n🔄 STEP {iterations} OF {max_steps}")

        messages = memory_manager.prune_messages(messages)

        response = agent_llm.complete(messages)

        # --- TRACK TOKENS & LATENCY ---
        if hasattr(response, 'usage') and response.usage:
            metrics["tokens"] += getattr(response.usage, 'total_tokens', 0)
            metrics["prompt_tokens"] += getattr(response.usage, 'prompt_tokens', 0)
            metrics["completion_tokens"] += getattr(response.usage, 'completion_tokens', 0)
            metrics["queue_time"] += getattr(response.usage, 'queue_time', 0.0)
            metrics["prompt_time"] += getattr(response.usage, 'prompt_time', 0.0)
            metrics["completion_time"] += getattr(response.usage, 'completion_time', 0.0)
            metrics["total_time"] += getattr(response.usage, 'total_time', 0.0)
        # ------------------------------

        llm_text = response.choices[0].message.content

        messages.append({"role": "assistant", "content": llm_text})

        print(f"🤖 LLM Response: {llm_text}")

        try:
            parsed_output = parse_llm_output(llm_text)
            print(f"✅ Parsed Output: {parsed_output}")
        except Exception as e:
            print(f"❌ Parsing Error: {str(e)}")
            messages.append({"role": "user", "content": f"Observation: ERROR - {str(e)}"})
            continue

        action, action_input = parsed_output

        if action == "Final Answer":
            print(f"🔄 Final Answer: {action_input}")
            metrics["iterations"] = iterations
            return {"messages": messages, "metrics": metrics}

        print(f"🔄 Taking Action: {action}")
        print(f"🔄 Action Input: {action_input}")

        try:
            result = TOOL_REGISTRY[action](**action_input)
        except Exception as e: 
            print(f"Tool call error: {str(e)}")
            messages.append({"role": "user", "content": f"Tool Call: ERROR - {str(e)}"})
            continue

        print(f"Observation: {result}")
        messages.append({"role": "user", "content": f"Observation: {result}"})
        print(f"🔄 Result: {result}")
    
    metrics["iterations"] = iterations
    return {"messages": messages, "metrics": metrics}