from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Config:
    @staticmethod
    def initialize_session_states(self):
        """Initialize all session state variables"""
        # Model configurations
        if "llm" not in st.session_state:
            st.session_state.llm = ChatGroq(
                temperature=self.get_config()["temperature"], 
                model_name=self.get_config()["model_name"],
            )

        if "model" not in st.session_state:
            st.session_state.model = self.get_config()["model_name"]

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
            "temperature": 0,
            "default_name": "New Chat",
        }