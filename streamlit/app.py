import streamlit as st

def fetch_response(prompt: str) -> str:
    return "Hello I'm a cute bot!"

st.title("Coffee Quality page")

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