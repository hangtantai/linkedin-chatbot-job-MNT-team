# import necessary file
import streamlit as st
import sys
import os
from pymongo import MongoClient 
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

# import external file
from streamlit_app.utils.config import Config

# Intilize configuration
config = Config()
config.initialize_session_states()
# Variables
db_uri = config.get_config()["db_uri"]
default_title = config.get_config()["default_name"]
max_word = config.get_config()["max_word"]


class DBHandler:
    """
    Connect to Mongo Atlas to manage history
    """
    def __init__(self):
        self.mongo_client = MongoClient(db_uri)
        self.db = self.mongo_client['chatbot']
        self.chat_collection = self.db['chat_history']
    
    def create_chat(self, chat_id: str, messages: list = None,  title: str = default_title) -> None:
        """
        Create a new chat document in the database
        
        Args:
            chat_id (str): The chat id
            messages (list): A list of messages
            title (str): The chat title
        """
        self.chat_collection.insert_one(
            {
                "_id": chat_id,
                "title": title,
                "messages": messages if messages else []
            }
        )
    
    def get_chat(self, chat_id: str) -> dict:
        """
        Get a chat document from the database
        
        Args:
            chat_id (str): The chat id
        
        Returns:
            dict: The chat document
        """
        return self.chat_collection.find_one({"_id": chat_id})

    def update_chat_messages(self, chat_id: str, messages: list) -> None:
        """
        Update the messages in a chat document
        
        Args:
            chat_id (str): The chat id
            messages (list): A list of messages
        """
        self.chat_collection.update_one(
            {"_id": chat_id},
            {"$push": {"messages": messages}}
        )
    
    def insert_chat_message(self, chat_id: str, messages: dict, title: str) -> None:
        """
        Insert a message into a chat document
        
        Args:
            chat_id (str): The chat id
            message (dict): The message dictionary
        """
        self.chat_collection.insert_one(
            {
                "_id": chat_id,
                "messages": messages,
                "title": title[:max_word] + "..." if len(title) > max_word else title  # Use first message as title
            }
        )
    
    def update_chat_title(self, chat_id: str, new_title: str) -> None:
        """
        Update the title of a chat document
        
        Args:
            chat_id (str): The chat id
            new_title (str): The new title
        """
        self.chat_collection.update_one(
            {"_id": chat_id},
            {"$set": {"title": new_title}}
        )
    
    def delete_chat(self, chat_id: str) -> None:
        """
        Delete a chat document from the database
        
        Args:
            chat_id (str): The chat id
        """
        self.chat_collection.delete_one({"_id": chat_id})
    
    def get_all_chats(self, sort_by: str = "_id", order: int = -1) -> list:
        """
        Get all chat documents, sorted by the specified field.
        
        Args:
            sort_by (str): The field to sort by
            order (int): The sort order (1 for ascending, -1 for descending)
        
        Returns:
            list: A list of chat documents
        """
        return self.chat_collection.find().sort(sort_by, order)

    def get_chat_title(self, chat: dict) -> str:
        """
        Get chat title from first message or return default title.
        Args:
            chat (dict): The chat document
        
        Returns:
            str: The chat title
        """
        messages = chat.get("messages", [])
        if messages:
            first_message = messages[0].get("content", "")
            words = first_message.split()[:max_word]
            title = " ".join(words)
            if len(words) < len(first_message.split()):
                title += "..."
            return title
        return chat.get("title", default_title)