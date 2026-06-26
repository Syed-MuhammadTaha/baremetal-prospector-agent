from .context import get_system_prompt
import tools  # noqa: F401 — ensure tools are registered for execution
from tools.registry import TOOL_REGISTRY
from .parser import parse_llm_output
from .llm import agent_llm
from .memory import ShortTermManager
import time

def run_agent(query: str, chat_history: list = None, max_steps: int = 10, ui_mode: str = "cli"):
    """The core execution engine of the autonomous agent."""
    print(f"\n🚀 INITIALIZING AGENT FOR: {query}")
    start_time = time.time()
    
    # --- METRICS ACCUMULATORS ---
    cumulative_tokens = 0
    cumulative_llm_time = 0.0
    
    # 1. Assemble the rules and tools
    system_prompt = get_system_prompt()

    print("System prompt loaded.")
    print("-" * 40)
    
    # 2. Initialize Working Memory (The State)
    if chat_history is None:
        messages = [{"role": "system", "content": system_prompt}]
    else:
        messages = chat_history
        messages[0]["content"] = system_prompt
        
    if query:
        messages.append({"role": "user", "content": query})

    print("✅ Context Assembled. State Initialized.")
    print("-" * 40)

    memory_manager = ShortTermManager(max_tail=6, chunk_size=4)
    
    for step in range(max_steps):
        print(f"\n🔄 STEP {step + 1} OF {max_steps}")

        messages = memory_manager.prune_messages(messages)

        # Call the LLM (Tracking latency natively if available)
        llm_start = time.time()
        response = agent_llm.complete(messages)
        llm_end = time.time()

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

        # Accumulate exact metrics from Groq if available
        if hasattr(response, 'usage') and response.usage:
            cumulative_tokens += response.usage.total_tokens
            cumulative_llm_time += getattr(response.usage, "total_time", llm_end - llm_start)
        else:
            cumulative_llm_time += (llm_end - llm_start)

        metrics = {
            "iterations": step + 1,
            "tokens": cumulative_tokens,
            "total_time": cumulative_llm_time,
            "wall_time": time.time() - start_time
        }

        # --- 1. COMPLETION CONDITION ---
        if action == "Final Answer":
            print(f"🔄 Final Answer: {action_input}")
            return {
                "status": "complete",
                "messages": messages,
                "metrics": metrics
            }

        # --- 2. STREAMLIT HITL INTERCEPTION ---
        # If the UI is Streamlit, do NOT run the terminal tool. Return to UI instead.
        if action == "ask_human" and ui_mode == "streamlit":
            question = action_input.get("question", "I need your input to proceed.")
            print(f"⏸️ PAUSING FOR STREAMLIT HUMAN INPUT: {question}")
            return {
                "status": "ask_human",
                "question": question,
                "messages": messages,
                "metrics": metrics
            }

        # --- 3. STANDARD TOOL EXECUTION ---
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
    
    # Fallback if max steps reached
    return {
        "status": "complete",
        "messages": messages,
        "metrics": {"iterations": max_steps, "tokens": 0, "total_time": time.time() - start_time}
    }