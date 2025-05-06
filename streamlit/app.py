import streamlit as st
import requests
import json
import re

API_URL = 'http://localhost:11434/api/chat'

# Prompt engineering: https://arize.com/blog-course/mastering-openai-api-tips-and-tricks/

def fetch_response(prompt: str) -> str:

    traits = st.session_state.get("traits", "")
    task = st.session_state.get("task", "")
    tone = st.session_state.get("tone", "")
    target = st.session_state.get("target", "")

    system = (

        f"Traits: {traits}\n"
        f"Task: {task}\n"
        f"Tone: {tone}\n"
        f"Target: {target}"
    )


    body = {
        "model": "deepseek-r1:1.5b",
        "messages": [
            {"role": "system", "content": system,
            },
            {"role": "user", "content": prompt}
        ]
    }


    try:

        res = requests.post(API_URL, json=body)

        if res.status_code == 200:

            response_parts = res.text.strip().split("\n")

            response = []

            for part in response_parts:

                try:
                    response_json = json.loads(part)
                    response.append(response_json['message']['content'])
                except json.JSONDecodeError:
                    continue

            final_response = ''.join(response)

            final_response = re.sub(r'<think>', '', final_response)
            final_response = re.sub(r'</think>', '', final_response)

            return final_response.strip()

        
        else:

            return f"Error. Try again"
    
    except requests.exceptions.RequestException as e:

        return f"Error connecting to API"

# Sidebar with prompt settings 

st.sidebar.title("Prompt engineering")

with st.sidebar.form("form"):
    
    traits = st.text_area("Traits", "")
    task = st.text_area("Task", "")
    tone = st.text_area("Tone", "")
    target = st.text_area("Target", "")

    submitted = st.form_submit_button("Save")
    
    if submitted:
        st.session_state["traits"] = traits
        st.session_state["task"] = task
        st.session_state["tone"] = tone
        st.session_state["target"] = target
        
        st.sidebar.success("Settings have been saved")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Prompt The Bot"):

    with st.chat_message("user"):
        st.markdown(prompt)   
    
    # TODO: Fetch response from bot
    response = fetch_response(prompt)

    with st.chat_message("bot"):
        st.markdown(response)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "bot", "content": response})