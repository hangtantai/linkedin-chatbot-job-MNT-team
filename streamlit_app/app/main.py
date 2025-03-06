import streamlit as st
from bson.objectid import ObjectId
import os
import sys
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

from streamlit_app.utils.config import Config
from streamlit_app.app.sidebar import SidebarComponent
from streamlit_app.handlers.db_handler import DBHandler
from streamlit_app.handlers.chat_handler import ChatHandler 
from streamlit_app.handlers.session_handler import SessionHandler
from streamlit_app.helpers.processing_text import escape_for_js
from streamlit_app.handlers.style_loader_handler import StyleLoader

# Initialize configuration
config = Config()
config.initialize_session_states()

# Load styles and scripts
StyleLoader.load_css([
    config.get_config()["folder_css"],
])
StyleLoader.load_js([
   config.get_config()["folder_js"],
])

# Intilize chat handler
if 'handler_initialized' not in st.session_state:
    st.session_state.handler_initialized = False

# Create a status check function
def check_initialization_status():
    # Get the chat handler from session state
    chat_handler = st.session_state.chat_handler
    
    # Check if initialization status has changed
    if chat_handler.is_ready and not st.session_state.handler_initialized:
        st.session_state.handler_initialized = True
        st.rerun()  

# Initialize chat handler (this won't block now)
if 'chat_handler' not in st.session_state:
    st.session_state.chat_handler = ChatHandler()

# Add a periodic status checker that runs every few seconds
if not st.session_state.handler_initialized:
    check_initialization_status()
    
    #  Add auto-refresh using JavaScript
    st.markdown(
        """
        <script>
        if (!window.init_refresh_set) {
            window.init_refresh_set = true;
            setTimeout(function() {
                window.location.reload();
            }, 3000);  // Check every 3 seconds
        }
        </script>
        """,
        unsafe_allow_html=True
    )

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

# Display initialization status
chat_handler = st.session_state.chat_handler

if st.button("🔄 Refresh Chatbot"):
    st.rerun()

if not chat_handler.is_ready:
    st.info("🔄 The chatbot is initializing. You can browse the interface but chat will be available shortly...")

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

# Chat input - disable if not ready
input_placeholder = "Type your message here..."
if not chat_handler.is_ready:
    input_placeholder = "Please wait while the system initializes..."

# Process user input
if prompt := st.chat_input(input_placeholder, disabled=not chat_handler.is_ready):
    # Check if this is a new chat
    if st.session_state.chat_id is None:
        # Create new chat only when first message is sent
        new_chat_id = ObjectId()
        st.session_state.chat_id = str(new_chat_id)
        db_handler.insert_chat_message(
            chat_id=new_chat_id,
            messages=[],
            title=prompt
        )

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Force a rerun to show the user message immediately
    st.rerun()

# Check if we need to process a response (after the rerun)
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user" and chat_handler.is_ready:
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Get the last user message
            user_message = st.session_state.messages[-1]["content"]
            
            with st.spinner("Thinking..."):
                # Generate response
                response_content = chat_handler.retrieve_qa(user_message)
                
                # Stream the response
                chat_handler.stream_response(response_content, message_placeholder)
                
                # Add assistant response to messages
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                
                # Update MongoDB
                current_chat_id = ObjectId(st.session_state.chat_id)
                db_handler.update_chat_messages(current_chat_id, {"role": "user", "content": user_message})
                db_handler.update_chat_messages(current_chat_id, {"role": "assistant", "content": response_content})
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {str(e)}"})