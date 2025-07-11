import streamlit as st
import requests
import json
import os
from datetime import datetime

# Load environment variables from .env file
import dotenv
dotenv.load_dotenv()

st.set_page_config(page_title="AI Research Assistant", layout="centered")

st.title("🤖 Dwayne AI Research Assistant")
st.markdown("Ask me anything about Transformers, Attention Mechanisms, or recent ML papers!")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.success("Chat history cleared.")

    if st.session_state.messages:
        if st.download_button(
            label="⬇️ Export Chat as JSON",
            data=json.dumps(st.session_state.messages, indent=2),
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        ):
            st.success("Chat exported as JSON.")

        transcript = "\n\n".join([
            f"You ({m.get('timestamp', 'unknown')}): {m['content']}" if m["role"] == "user"
            else f"Dwayne AI ({m.get('timestamp', 'unknown')}): {m['content']}"
            for m in st.session_state.messages
        ])
        if st.download_button(
            label="⬇️ Export Chat as Text",
            data=transcript,
            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        ):
            st.success("Chat exported as Text.")

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        timestamp = msg.get("timestamp")
        if timestamp:
            st.markdown(f"<sub>{timestamp}</sub>", unsafe_allow_html=True)
        st.markdown(msg["content"])

# User prompt input
if prompt := st.chat_input("Type your research question..."):
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp_now})
    with st.chat_message("user"):
        st.markdown(f"<sub>{timestamp_now}</sub>", unsafe_allow_html=True)
        st.markdown(prompt)

    with st.spinner("Thinking..."):
        try:
            base_url = os.getenv("GENAI_API_URL")
            access_key = os.getenv("AGENT_ACCESS_KEY")
            if not base_url or not access_key:
                st.error("❌ Missing GENAI_API_URL or AGENT_ACCESS_KEY in environment.")
            else:
                # Append the correct path for chat completions
                url = base_url.rstrip("/") + "/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {access_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "messages": st.session_state.messages,
                    "stream": False,
                    "include_functions_info": False,
                    "include_retrieval_info": False,
                    "include_guardrails_info": False
                }

                res = requests.post(url, json=payload, headers=headers)
                res.raise_for_status()
                response_data = res.json()
                answer = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No answer returned.")

                timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with st.chat_message("assistant"):
                    st.markdown(f"<sub>{timestamp_now}</sub>", unsafe_allow_html=True)
                    st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "timestamp": timestamp_now
                })

        except Exception as e:
            st.error(f"❌ Error: {e}")
