import os 
from dotenv import load_dotenv
from pymongo import MongoClient 
load_dotenv()


class DBHandler:
    def __init__(self):
        self.mongo_client = MongoClient(os.environ['MONGO_URI'])
        self.db = self.mongo_client['chatbot']
        self.chat_collection = self.db['chat_history']
    
    def create_chat(self, chat_id: str, messages: list = None,  title: str = "New chat") -> None:
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
            {"$set": {"messages": messages}}
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
            words = first_message.split()[:15]
            title = " ".join(words)
            if len(words) < len(first_message.split()):
                title += "..."
            return title
        return chat.get("title", "New Chat")