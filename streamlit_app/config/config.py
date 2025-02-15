from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Config:
    @staticmethod
    def initialize_session_states():
        """Initialize all session state variables"""
        # Model configurations
        if "llm" not in st.session_state:
            st.session_state.llm = ChatGroq(
                temperature=0, 
                model_name="llama3-70b-8192",
            )

        if "model" not in st.session_state:
            st.session_state.model = "llama3-70b-8192"

        # Chat states
        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "chat_id" not in st.session_state:
            st.session_state.chat_id = None

    @staticmethod
    def get_config():
        """Get general configuration values"""
        return {
            "time_sleep": 0.02,
            "max_word": 15,
            "model_name": "llama3-70b-8192",
            "temperature": 0
        }