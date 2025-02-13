import streamlit as st
from app.services.upload import upload_service
from app.services.chat import chat_service
import asyncio

st.title("💬 Retail Leases AI - Assistant")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

# Add file uploader in the sidebar
with st.sidebar:
    st.header("CSV Upload")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    if uploaded_file is not None:
        try:
            with st.spinner('Processing CSV file...'):
                upload_service.process_csv(uploaded_file)
            st.success('CSV file successfully processed and stored in databases!')
        except Exception as e:
            st.error(f'Error processing file: {str(e)}')

# Chat interface
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are helpful assistant to assist user providing information about retail leases."},
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = chat_service.process_message(prompt, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)