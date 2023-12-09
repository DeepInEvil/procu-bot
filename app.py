import streamlit as st
import os
import pandas as pd
from ctransformers import AutoModelForCausalLM
from db2kg import get_unspc, get_kg_triple

unspc, ents = get_unspc('data/data-unspsc-codes.csv')
# pencil_data = 'pencil region east \n pencil price 4.99 \n pencil region central \n pencil price 1.29 \n pencil region west \n pencil price 1.99 '
# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

@st.cache_resource()
def ChatModel(temperature, top_p):
    return AutoModelForCausalLM.from_pretrained(
        'data/llama-2-7b-chat.ggmlv3.q2_K.bin',
        model_type='llama',
        temperature=temperature, 
        top_p = top_p)

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')

    # Refactored from <https://github.com/a16z-infra/llama2-chatbot>
    st.subheader('Models and parameters')
    
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=2.0, value=0.6, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.5, step=0.01)
    # max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)
    chat_model =ChatModel(temperature, top_p)
    # st.markdown('📖 Learn how to build this app in this [blog](#link-to-blog)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():

    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

def get_prompt(query):
    print('query: ', query)
    _data = get_kg_triple(query, ents, unspc)
    string_dialogue = "You are a procurement assistant helping people with unspc. You respond to the Customer: using data " + _data + \
                      "\n You only respond as Assistant."
    return string_dialogue
# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue = get_prompt(dict_message["content"])
            print('sd: ', string_dialogue)
            string_dialogue += "Customer: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue = "You are a procurement assistant. You respond to the Customer: about the data " \
                              " You only respond as Assistant."
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"
    output = chat_model(f"prompt {string_dialogue} {prompt_input} Assistant: ")
    return output.split('Customer:')[0].split('\n')[0]

# User-provided prompt
if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
