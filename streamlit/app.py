import streamlit as st
import requests
import json
import re
import pandas as pd


API_URL = 'http://localhost:11434/api/chat'

# Prompt engineering: https://arize.com/blog-course/mastering-openai-api-tips-and-tricks/

def fetch_response(prompt: str) -> str:

    traits = st.session_state.get("traits", "")
    task = st.session_state.get("task", "")
    tone = st.session_state.get("tone", "")
    target = st.session_state.get("target", "")
    desc_str = st.session_state.get("desc", "")
    corr_str = st.session_state.get("corr", "")
    sample_str = st.session_state.get("sample", "")

    if isinstance(desc_str, pd.DataFrame) and isinstance(corr_str, pd.DataFrame) and isinstance(sample_str, pd.DataFrame):
        desc_str = desc_str.to_csv(index=False)
        corr_str = corr_str.to_csv(index=False)
        sample_str = sample_str.to_csv(index=False)


    system = (

        f"Traits: {traits}\n"
        f"Task: {task}\n"
        f"Tone: {tone}\n"
        f"Target: {target}\n"
        f"Dataset Descriptive Statistics: {desc_str}\n"
        f"Dataset Correlation Matrix: {corr_str}\n"
        f"Dataset Sample: {sample_str}"
            
    )

    full_prompt = f"""
You are provided a user prompt and a context.
Use the context as a basis for answering the user prompt as good as you can.
Respond acting as is specified in "Traits".
Respond like youre addressing what is specified in "Target".

Dataset information is provided as a Sample, Correlation Matrix and Descriptive Statistics.
They represent a Pandas Dataframe.
Use this as a background for responding.

Only consider the context if it is provided explicitly

Context:
{system}

User Prompt:
{prompt}
"""

    body = {
        "model": "deepseek-r1:1.5b",
        "messages": [
           # {"role": "system", "content": system,
           #},
            {"role": "user", "content": full_prompt}
        ]
    }

    st.write(body)


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
    
    traits = st.text_area("Traits", f'{st.session_state.get("traits", "")}')
    task = st.text_area("Task", f'{st.session_state.get("task", "")}')
    tone = st.text_area("Tone", f'{st.session_state.get("tone", "")}')
    target = st.text_area("Target", f'{st.session_state.get("target", "")}')

    uploaded_file = st.file_uploader("Clean Dataset")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        sample = df.sample(5)
        desc = df.describe()
        corr = df.corr()
        st.dataframe(sample)
        st.dataframe(desc)
        st.dataframe(corr)

    submitted = st.form_submit_button("Save")
    
    if submitted:
        st.session_state["traits"] = traits
        st.session_state["task"] = task
        st.session_state["tone"] = tone
        st.session_state["target"] = target
        st.session_state["desc"] = desc
        st.session_state["corr"] = corr
        st.session_state["sample"] = sample
        
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