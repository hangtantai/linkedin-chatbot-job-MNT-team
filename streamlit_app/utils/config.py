from langchain_groq import ChatGroq
import streamlit as st
import os
import sys
import pymysql
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
api_key = st.secrets["GROQ_API_KEY"]
class Config:
    _config = {
        "time_sleep": 0.02,
        "max_word": 15,
        "model_name": "llama3-70b-8192",
        "temperature": 0,
        "default_name": "New Chat",
        "env_filename": ".env",
        "app_folder": "streamlit_app",
        "folder_css": "streamlit_app/static/styles.css",
        "folder_js": "streamlit_app/static/scripts.js",
        "auto_refresh": "streamlit_app/static/js/auto_refresh.js",
        "copy_handler": "streamlit_app/static/js/copy_handler.js",
        "max_tokens": 1500,
        "assistant_message_row": 3,
        "defaul_model_token": "cl100k_base",
        "DB_config": {
                "host": st.secrets["HOST_AIVEN"],
                "user": st.secrets["USER_AIVEN"],
                "password": st.secrets["PASSWORD_AIVEN"],
                "db": st.secrets["DB_AIVEN"],
                "port": int(st.secrets["PORT_AIVEN"]),
                "charset": "utf8mb4",
                # "cursorclass": pymysql.cursors.DictCursor,
                "connect_timeout": 10,
                "read_timeout": 10,
                "write_timeout": 10,
            },
        "table_name": st.secrets["TABLE_AIVEN"],
        "vector_db_path": "streamlit_app/db/vector_db",
        "model_name_vectordb": "sentence-transformers/all-MiniLM-L6-v2",
        "cache_folder": "streamlit_app/models/vector_db/"
    }

    @classmethod
    def initialize_session_states(cls):
        """Initialize all session state variables"""
        # Model configurations
        if "llm" not in st.session_state:
            st.session_state.llm = ChatGroq(
                api_key=api_key,
                temperature=cls.get_config()["temperature"], 
                model_name=cls.get_config()["model_name"],
            )

        if "model" not in st.session_state:
            st.session_state.model = cls.get_config()["model_name"]

        # Chat states
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "chat_id" not in st.session_state:
            st.session_state.chat_id = None

    @classmethod
    def get_config(cls):
        """Get general configuration values"""
        return cls._config.copy()