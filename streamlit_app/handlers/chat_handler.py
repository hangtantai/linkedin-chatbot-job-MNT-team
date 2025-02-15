from langchain_groq import ChatGroq
import streamlit as st
import time
from typing import List, Dict, Any
from streamlit_app.config.config import Config

# Initialize configuration
config = Config()

# Initialize configuration
config.initialize_session_states()

# variables
time_sleep_var = config.get_config()["time_sleep"]
temperature_var = config.get_config()["temperature"]
model_name_var = config.get_config()["model_name"]

class ChatHandler:
    def __init__(self, model_name: str = model_name_var, temperature: int = temperature_var):
        self.groq = ChatGroq(model_name=model_name, temperature=temperature)
        self.time_sleep = time_sleep_var


    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using the chat model
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
        
        Returns:
            str: Generated response
        """
        try:
            response = self.llm.invoke(input=messages)
            return response.content
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "" 
    
    def stream_response(self, response: str, placeholder: Any) -> None:
        """
        Stream the response with typing effect
        
        Args:
            response (str): Response text to stream
            placeholder: Streamlit placeholder for displaying response
        """
        full_response = ""
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(self.time_sleep)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
    
    def format_messages_for_model(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format messages for model input
        
        Args:
            messages (List[Dict[str, str]]): Raw messages from chat history
        
        Returns:
            List[Dict[str, str]]: Formatted messages for model
        """
        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in messages
        ]

    def validate_message(self, message: str) -> bool:
        """
        Validate user message
        
        Args:
            message (str): User input message
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not message or not message.strip():
            return False
        return True

    @staticmethod
    def create_message(role: str, content: str) -> Dict[str, str]:
        """
        Create a message dictionary
        
        Args:
            role (str): Message role (user/assistant)
            content (str): Message content
        
        Returns:
            Dict[str, str]: Formatted message dictionary
        """
        return {
            "role": role,
            "content": content
        }