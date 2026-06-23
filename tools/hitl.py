from .registry import tool
@tool
def ask_human(question: str) -> str:
    """
    Pauses the agent loop and asks the human operator a question via the terminal.
    Returns the human's typed response.
    """
    print("\n" + "🛑 "*20)
    print("✋ [AGENT ESCALATION] The agent needs your input:")
    print(f"❓ Agent: {question}")
    
    # This pauses the Python script and waits for you to type
    answer = input("👤 Your Answer: ")
    print("🛑 "*20 + "\n")
    
    return f"Human response: {answer}"