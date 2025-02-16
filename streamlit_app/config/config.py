from langchain_groq import ChatGroq
import streamlit as st
import os
import sys
if "C:\\Users\\Hang Tan Tai\\AppData\\Local\\Programs\\Python\\Python311\\Lib" not in sys.path:
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
# from streamlit_app.helpers.load_env import load_env_file
# from streamlit_app.helpers.load_env_secret import get_env_var
# load_env_file(env_filename=".env", app_folder="streamlit_app")
# api_key = get_env_var("GROQ_API_KEY")
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