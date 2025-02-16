from bson.objectid import ObjectId
from pymongo.collection import Collection
import streamlit as st
import os
import sys
# Check if running on Streamlit Cloud

if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
from pymongo import MongoClient 
from streamlit_app.config.config import Config
from typing import Any

# intilize configuration
config = Config()

# default title
default_title = config.get_config()["default_name"]

class SessionHandler:
    def __init__(self, chat_collection: Collection) -> None:
        """
        Initialize SessionHandler with MongoDB collection
        
        Args:
            chat_collection (Collection): MongoDB collection for chats
        """
        self.chat_collection = chat_collection
        self.session_state = st.session_state

    def create_new_chat(self) -> None:
        """
        Create a new chat and set it as the selected chat.
        """
        self.session_state.chat_id = str(ObjectId())
        self.session_state.messages = []
        self.chat_collection.insert_one({
            "_id": ObjectId(self.session_state.chat_id), 
            "messages": [],
            "title": default_title
        })
        if "selected_chat" in self.session_state:
            del self.session_state.selected_chat
        st.rerun()
        
    def switch_chat(self, chat_id: str) -> None:
        """
        Switch to a different chat by setting the chat_id and loading messages.

        Args:
            chat_id (str): The ID of the chat to switch to.
        """
        chat = self.chat_collection.find_one({"_id": ObjectId(chat_id)})
        if chat:
            self.session_state.messages = chat.get("messages", [])
            self.session_state.chat_id = str(chat_id)
            if "selected_chat" not in self.session_state:
                self.session_state.selected_chat = str(chat_id)
        st.rerun()

    def initialize_session_state(self) -> None:
        """
        Initialize all required session state variables
        """
        if "chat_id" not in self.session_state:
            self.session_state.chat_id = None
        
        if "messages" not in self.session_state:
            self.session_state.messages = []
    
    def show_rename(chat_id: str, current_title: str, chat_collection: MongoClient) -> None:
        """
        Show a popup to rename a chat in the sidebar.

        Args:
            chat_id (str): The ID of the chat to rename.
            current_title (str): The current title of the chat.
            chat_collection (MongoClient): The MongoDB collection
        """
        # show rename box
        if f"show_rename_{chat_id}" in st.session_state:
            with st.sidebar:
                new_title = st.text_input("Rename chat", current_title, key=f"rename_input_{chat_id}")
                # split into two columns
                col1, col2 = st.columns([1, 1])
                
                # save button in rename box
                with col1:
                    if st.button("Save", key=f"save_rename_{chat_id}"):
                        chat_collection.update_one({"_id": ObjectId(chat_id)}, {"$set": {"title": new_title}})
                        st.session_state.pop(f"show_rename_{chat_id}", None)
                        st.session_state.sidebar_updated = True
                        st.rerun()
                
                # cancel button in rename box
                with col2:
                    if st.button("Cancel", key=f"cancel_rename_{chat_id}"):
                        st.session_state.pop(f"show_rename_{chat_id}", None)
                        st.rerun()
    def process_knowledge(self, session_state: Any) -> dict:
        """
        Process all previous chat messages to model

        Args:
            session_state (Any): Streamlit session state
        """
        chat_context = []
        for msg in session_state.messages[:-1]: 
            chat_context.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return chat_context