import streamlit as st
from bson.objectid import ObjectId
import os
import sys

if "C:\\Users\\Hang Tan Tai\\AppData\\Local\\Programs\\Python\\Python311\\Lib" not in sys.path:
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

from streamlit_app.config.config import Config
from streamlit_app.app.sidebar import SidebarComponent
from streamlit_app.handlers.db_handler import DBHandler
from streamlit_app.handlers.chat_handler import ChatHandler 
from streamlit_app.handlers.session_handler import SessionHandler
from streamlit_app.helpers.processing_text import escape_for_js
from streamlit_app.handlers.style_loader_handler import StyleLoader
from streamlit_app.helpers.load_env import load_env_file

# Initialize configuration
config = Config()
config.initialize_session_states()

# load_env_file(env_filename=config.get_config()["env_filename"], app_folder=config.get_config()["app_folder"])

# Load styles and scripts
StyleLoader.load_css([
    config.get_config()["folder_css"],
])
StyleLoader.load_js([
   config.get_config()["folder_js"],
])

# Intilize chat handler
chat_handler = ChatHandler()

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
        db_handler.insert_chat_message(
            chat_id = new_chat_id,
            messages = [],
            title = prompt
        )

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Create context from all previous messages
            chat_context = session_handler.process_knowledge(st.session_state)
            
            # Add the current message
            chat_context.append({
                "role": "user",
                "content": prompt
            })

            response_content = chat_handler.generate_response(chat_context)
            
            # Stream the response
            chat_handler.stream_response(response_content, message_placeholder)
            
            # Add assistant response to messages
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            
            # Update MongoDB
            current_chat_id = ObjectId(st.session_state.chat_id)
            db_handler.update_chat_messages(current_chat_id, {"role": "user", "content": prompt})
            db_handler.update_chat_messages(current_chat_id, {"role": "assistant", "content": response_content})
            # db_handler.chat_collection.update_one(
            #     {"_id": current_chat_id},
            #     {
            #         "$push": {
            #             "messages": {
            #                 "$each": [
            #                     {"role": "user", "content": prompt},
            #                     {"role": "assistant", "content": response.content}
            #                 ]
            #             }
            #         }
            #     }
            # )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            message_placeholder.markdown("Sorry, there was an error generating the response. Please try again.")