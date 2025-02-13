from config import load_env
from src.agents.graph_agent import Agent
import streamlit as st
from src.tools.vectordb_utils import import_csv_to_vector
from src.tools.db_utils import import_csv_to_mysql
import tempfile
import os

load_env()

agent = Agent()
st.title("💬 Retail Leases AI - Assistant")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

# Add file uploader in the sidebar
with st.sidebar:
    st.header("CSV Upload")
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            # Write the uploaded file content to temporary file
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            with st.spinner('Processing CSV file...'):
                import_csv_to_vector(tmp_file_path)
                import_csv_to_mysql(tmp_file_path)
            st.success('CSV file successfully processed and stored in vector database!')
        except Exception as e:
            st.error(f'Error processing file: {str(e)}')
        finally:
            # Clean up the temporary file
            os.unlink(tmp_file_path)

# Chat interface
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are helpful assistant to assist user providing information about retail leases."},
        {"role": "assistant", "content": "How can I help you?"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    msg = agent.invoke(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)