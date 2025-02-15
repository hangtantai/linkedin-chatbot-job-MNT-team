import os 
import time
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient 
from bson.objectid import ObjectId
from langchain_groq import ChatGroq
from streamlit_app.handler.db_handler import DBHandler
from streamlit_app.config.config import Config
from streamlit_app.handler.session_handler import SessionHandler
from streamlit_app.app.sidebar import SidebarComponent
from streamlit_app.helper.helper_ui import escape_for_js
from streamlit_app.helper.style_loader import StyleLoader

# Load styles and scripts
StyleLoader.load_css([
    'streamlit_app/static/styles.css',
])
StyleLoader.load_js([
    'streamlit_app/static/scripts.js'
])

load_dotenv()

# Initialize configuration
config = Config()
config.initialize_session_states()

# Define variables
time_sleep = config.get_config()["time_sleep"]
max_word = config.get_config()["max_word"]

# Initialize DB handler
db_handler = DBHandler()

# Initialize session handler
session_handler = SessionHandler(db_handler.chat_collection)

# Initialize sidebar component
sidebar = SidebarComponent(
    chat_collection=db_handler.chat_collection,
    create_new_chat=session_handler.create_new_chat,
    switch_chat=session_handler.switch_chat,
    get_chat_title=db_handler.get_chat_title,
    show_rename=session_handler.show_rename
)

# Main app title
st.title("Chatbot MNT team")
sidebar.render()

# Main chat area
# Update the message display section
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            escaped_content = escape_for_js(message["content"])
            st.markdown(
                f"""
                <div class="message-container">
                    {message["content"]}
                    <button class="copy-button" onclick="copyToClipboard('{escaped_content}')">
                        📋 Copy
                    </button>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Check if this is a new chat
    if st.session_state.chat_id is None:
        # Create new chat only when first message is sent
        new_chat_id = ObjectId()
        st.session_state.chat_id = str(new_chat_id)
        db_handler.chat_collection.insert_one({
            "_id": new_chat_id,
            "messages": [],
            "title": prompt[:30] + "..." if len(prompt) > 30 else prompt  # Use first message as title
        })

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Create context from all previous messages
            chat_context = []
            for msg in st.session_state.messages[:-1]: 
                chat_context.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            # Add the current message
            chat_context.append({
                "role": "user",
                "content": prompt
            })

            response = st.session_state.llm.invoke(
                input=chat_context
            )
            
            # Stream the response
            full_response = ""
            for chunk in response.content.split():
                full_response += chunk + " "
                time.sleep(time_sleep)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            # Add assistant response to messages
            st.session_state.messages.append({"role": "assistant", "content": response.content})
            
            # Update MongoDB
            current_chat_id = ObjectId(st.session_state.chat_id)
            db_handler.chat_collection.update_one(
                {"_id": current_chat_id},
                {
                    "$push": {
                        "messages": {
                            "$each": [
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": response.content}
                            ]
                        }
                    }
                }
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            message_placeholder.markdown("Sorry, there was an error generating the response. Please try again.")

