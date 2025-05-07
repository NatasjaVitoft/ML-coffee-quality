import streamlit as st
import requests
import json
import re

API_URL = 'http://localhost:11434/api/chat'

def fetch_response(prompt: str) -> str:

    body = {
        "model": "deepseek-r1:1.5b",  
        "messages": [{
            "role": "user", 
            "content": prompt
        }]
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

st.title("Deep Seek")

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