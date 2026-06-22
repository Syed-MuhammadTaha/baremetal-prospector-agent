from .context import get_system_prompt
import tools  # noqa: F401 — ensure tools are registered for execution
from tools.registry import TOOL_REGISTRY
from .parser import parse_llm_output
from .llm import agent_llm
from .memory import ShortTermManager

def run_agent(query: str, max_steps: int = 10):
    """The core execution engine of the autonomous agent."""
    print(f"\n🚀 INITIALIZING AGENT FOR: {query}")
    
    # 1. Assemble the rules and tools
    system_prompt = get_system_prompt()

    print(f"System prompt: {system_prompt}")
    print("-" * 40)
    # 2. Initialize Working Memory (The State)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    print("✅ Context Assembled. State Initialized.")
    print("-" * 40)

    memory_manager = ShortTermManager(max_tail=6, chunk_size=4)
    for step in range(max_steps):
        print(f"\n🔄 STEP {step + 1} OF {max_steps}")

        messages = memory_manager.prune_messages(messages)

        response = agent_llm.complete(messages)


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
            return messages

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
    
    return messages

