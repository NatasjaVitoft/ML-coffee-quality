import streamlit as st
import requests
import json
import re
import pandas as pd


API_URL = 'http://localhost:11434/api/chat'

# Prompt engineering: https://arize.com/blog-course/mastering-openai-api-tips-and-tricks/

def fetch_response(prompt: str) -> str:

    traits = st.session_state.get("traits", "")
    target = st.session_state.get("target", "")
    desc_str = st.session_state.get("desc", "")
    corr_str = st.session_state.get("corr", "")
    sample_str = st.session_state.get("sample", "")

    if isinstance(desc_str, pd.DataFrame) and isinstance(corr_str, pd.DataFrame) and isinstance(sample_str, pd.DataFrame):
        desc_str = desc_str.to_csv(index=False)
        corr_str = corr_str.to_csv(index=False)
        sample_str = sample_str.to_csv(index=False)


    full_prompt = f"""
You are provided a user prompt and a context.
Use the context as a basis for answering the user prompt as good as you can.

All dataframe information is provided in CSV format, but represents a Pandas Dataframe.
Use this as a background for responding.

Only consider the context if it is provided explicitly

## Context:
Act like you are:
{traits}
You should be addressing:
{target}


### Dataset Sample
If present, this is a 5 row sample of the users dataset:
{sample_str}\n

### Dataset Descriptive Statitics
This is generated from the users dataframe using pandas df.describe().
the rows from top is: count, mean, standard deviation, mean, 25% quartile, 50% quartile
, 75% quartile, max:
{desc_str}\n

### Dataset Correlation Matrix.
This is generated from the users dataframe using pandas df.corr()
The rows represent the columns. the values is the correlation between features
{corr_str}\n

## User Prompt:
{prompt}
"""

    body = {
        "model": "deepseek-r1:7b",
        "messages": [
            {"role": "user", "content": full_prompt}
        ],
        "options": {
             "num_ctx": 12288,
        }
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
    
    traits = st.text_area("Traits and Tone", f'{st.session_state.get("traits", "")}')
    target = st.text_area("Target", f'{st.session_state.get("target", "")}')

    uploaded_file = st.file_uploader("Clean Dataset")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        sample = df.sample(5)
        desc = df.describe(include=[int, float, complex])
        corr = df.corr(numeric_only=True)
        st.dataframe(sample)
        st.dataframe(desc)
        st.dataframe(corr)

    submitted = st.form_submit_button("Save")
    
    if submitted:
        st.session_state["traits"] = traits
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
    st.session_state.messages.append({"role": "assistant", "content": response})