import os
from agent.engine import run_agent

def main():
    print("="*50)
    print("🤖 BAREMETAL PROSPECTOR INITIALIZED")
    print("Type 'exit' or 'quit' to shutdown.")
    print("="*50)

    # ---> CREATE THE PERSISTENT STATE HERE <---
    current_chat_history = None

    while True:
        # 1. The Terminal Prompt
        user_query = input("\n👤 You: ")
        
        # 2. Shutdown condition
        if user_query.lower() in ['exit', 'quit']:
            print("Shutting down the Prospector...")
            break
            
        # 3. Execute the agent and CAPTURE the updated history
        print("\n⚙️  Processing...")
        current_chat_history = run_agent(user_query, chat_history=current_chat_history)

if __name__ == "__main__":
    main()