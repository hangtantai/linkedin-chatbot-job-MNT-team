import streamlit as st
from bson.objectid import ObjectId
from typing import Callable
from pymongo.collection import Collection
class SidebarComponent:
    def __init__(self, 
                 chat_collection: Collection,
                 create_new_chat: Callable,
                 switch_chat: Callable,
                 get_chat_title: Callable,
                 show_rename: Callable):
        self.chat_collection = chat_collection
        self.create_new_chat = create_new_chat
        self.switch_chat = switch_chat
        self.get_chat_title = get_chat_title
        self.show_rename = show_rename

    def render(self):
        """Render the sidebar component"""
        with st.sidebar:
            st.title("Chat History")
            
            # New chat button
            if st.button("➕ New Chat", key="new_chat_btn", type="primary"):
                self.create_new_chat()
            
            st.markdown("---")

            # Check if sidebar needs to be updated after renaming
            if "sidebar_updated" in st.session_state:
                del st.session_state.sidebar_updated
                st.rerun()
            
            # Display chat history
            for idx, chat in enumerate(self.chat_collection.find().sort("_id", -1)):
                self._render_chat_item(idx, chat)

    def _render_chat_item(self, idx: int, chat: dict):
        """Render individual chat item in sidebar"""
        chat_id = chat.get("_id")
        title = self.get_chat_title(chat)

        chat_container = st.container()
        
        with chat_container:
            col1, col2 = st.columns([7, 3])
            
            # Chat title button
            with col1:
                button_key = f"chat_button_{idx}_{str(chat_id)}"
                if st.button(f"💬 {title}", key=button_key):
                    st.session_state.chat_id = str(chat_id)
                    self.switch_chat(chat_id)
            
            # Options dropdown
            with col2:
                self._render_chat_options(idx, chat_id, title)

    def _render_chat_options(self, idx: int, chat_id: ObjectId, title: str):
        """Render options dropdown for chat item"""
        option = st.selectbox(
            "Chat options",  
            ["⋮", "Rename", "Delete"],
            key=f"options_{idx}_{str(chat_id)}",
            label_visibility="collapsed"
        )
        
        if option == "Delete":
            if chat_id == st.session_state.chat_id:
                self.create_new_chat()
            self.chat_collection.delete_one({"_id": chat_id})
            st.rerun()
        
        elif option == "Rename":
            st.session_state[f"show_rename_{chat_id}"] = True
            self.show_rename(chat_id, title, self.chat_collection)
            st.rerun()