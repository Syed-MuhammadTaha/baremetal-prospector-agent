import streamlit as st
import json
from agent.engine import run_agent

st.set_page_config(page_title="Sable Prospector", page_icon="🤖", layout="wide")

def extract_dossier_content(messages):
    """Scans the conversation history to extract the final markdown dossier."""
    for msg in reversed(messages):
        if msg["role"] == "assistant" and "save_dossier" in msg.get("content", ""):
            try:
                text = msg["content"]
                start = text.find('{')
                end = text.rfind('}')
                data = json.loads(text[start:end+1], strict=False)
                return data.get("content", None)
            except Exception:
                continue
    return None

st.title("🤖 Sable Autonomous Prospector")
st.markdown("Enter a target company. The agent will research them, apply Sable's corporate memory, and draft a hyper-personalized cold email.")

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = None
if "chat_display" not in st.session_state:
    st.session_state.chat_display = []
if "waiting_for_human" not in st.session_state:
    st.session_state.waiting_for_human = False

# Sidebar for Reset
with st.sidebar:
    st.header("Control Panel")
    if st.button("🗑️ Reset Agent State", use_container_width=True):
        st.session_state.chat_history = None
        st.session_state.chat_display = []
        st.session_state.waiting_for_human = False
        st.rerun()

# Display Chat History
for chat in st.session_state.chat_display:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Input handling replacing the static st.form
user_input = st.chat_input("e.g., 'Research Gymshark' or answer the agent's question...")

if user_input:
    # 1. Display the user's message
    st.session_state.chat_display.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Format query based on HITL state
    if st.session_state.waiting_for_human:
        formatted_query = f"Observation: Human response: {user_input}"
        st.session_state.waiting_for_human = False
    else:
        formatted_query = user_input

    with st.chat_message("assistant"):
        with st.spinner("Agent is analyzing and acting..."):
            try:
                # Trigger the agent, passing the ui_mode flag to intercept terminal inputs
                result = run_agent(
                    query=formatted_query, 
                    chat_history=st.session_state.chat_history,
                    ui_mode="streamlit"
                )
                
                st.session_state.chat_history = result["messages"]
                metrics = result.get("metrics", {})
                status = result.get("status", "complete")

                # --- HITL ESCALATION ---
                if status == "ask_human":
                    st.session_state.waiting_for_human = True
                    question = result.get("question", "I need your input to proceed.")
                    st.warning(f"✋ Agent requires input: **{question}**")
                    st.session_state.chat_display.append({"role": "assistant", "content": f"✋ **I need your input:** {question}"})
                    st.rerun()
                
                # --- TASK COMPLETION ---
                else:
                    st.success("Task Completed!")
                    
                    # Display Metrics
                    if metrics:
                        cols = st.columns(3)
                        cols[0].metric("Loop Iterations", metrics.get("iterations", 0))
                        cols[1].metric("Tokens Used", metrics.get("tokens", 0))
                        cols[2].metric("Groq LLM Time", f"{metrics.get('total_time', 0):.2f}s")
                    
                    # Extract Dossier
                    dossier = extract_dossier_content(result["messages"])
                    
                    final_message = st.session_state.chat_history[-1]["content"]
                    final_answer = final_message.split("Final Answer:")[-1].strip() if "Final Answer:" in final_message else final_message
                    
                    if dossier:
                        st.markdown("### 📄 Final Drafted Dossier")
                        st.markdown(f"```markdown\n{dossier}\n```")
                        st.session_state.chat_display.append({
                            "role": "assistant", 
                            "content": f"✅ **Task Complete.** I drafted the email. Here is a preview:\n\n---\n{dossier}"
                        })
                    else:
                        st.markdown("### 📄 Final Output")
                        st.info(final_answer)
                        st.session_state.chat_display.append({
                            "role": "assistant", 
                            "content": f"✅ **Task Complete.**\n\n{final_answer}"
                        })

                    # Expander for debugging thought process
                    with st.expander("🔍 View Raw Agent Logs"):
                        for msg in st.session_state.chat_history:
                            if msg["role"] == "assistant":
                                st.markdown(f"**Agent:**\n```\n{msg['content']}\n```")
                            elif msg["role"] == "user":
                                st.markdown(f"**System/Observation:**\n{msg['content']}")
                                
            except Exception as e:
                st.error(f"Agent failed: {str(e)}")
                st.session_state.chat_display.append({"role": "assistant", "content": f"❌ **Error:** {str(e)}"})