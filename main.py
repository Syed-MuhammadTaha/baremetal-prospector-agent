import streamlit as st
from agent.engine import run_agent

st.set_page_config(page_title="Sable Prospector", page_icon="🤖", layout="centered")

st.title("🤖 Sable Autonomous Prospector")
st.markdown("Enter a target company. The agent will research them, apply Sable's corporate memory, and draft a hyper-personalized cold email.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = None

with st.form("prospect_form"):
    target_company = st.text_input("Target Company / Query", placeholder="e.g., 'Research Gymshark' or 'Rewrite the email to be more aggressive'")
    submit_button = st.form_submit_button("Launch Agent 🚀")

if submit_button and target_company:
    with st.spinner(f"Agent is analyzing {target_company}..."):
        try:
            result = run_agent(target_company, chat_history=st.session_state.chat_history)
            
            st.session_state.chat_history = result["messages"]
            metrics = result["metrics"]
            
            final_message = st.session_state.chat_history[-1]["content"]
            final_answer = final_message.split("Final Answer:")[-1].strip() if "Final Answer:" in final_message else final_message
            
            st.success("Task Completed!")
            
            cols = st.columns(3)
            cols[0].metric("Loop Iterations", metrics["iterations"])
            cols[1].metric("Tokens Used", metrics["tokens"])
            cols[2].metric("Groq LLM Time", f"{metrics['total_time']:.2f}s")
            
            # Display Output
            st.markdown("### 📄 Final Output / Email Draft")
            st.info(final_answer)
            
            # Expander for debugging thought process
            with st.expander("🔍 View Raw Agent Logs"):
                for msg in st.session_state.chat_history:
                    if msg["role"] == "assistant":
                        st.markdown(f"**Agent:**\n```\n{msg['content']}\n```")
                    elif msg["role"] == "user":
                        st.markdown(f"**System/Observation:**\n{msg['content']}")
                        
        except Exception as e:
            st.error(f"Agent failed: {str(e)}")