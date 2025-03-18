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

# Add a force rerun parameter
if "force_rerun" not in st.session_state:
    st.session_state.force_rerun = False

# Check URL parameters for force_rerun
if "rerun" in st.query_params:
    st.session_state.force_rerun = True
    # Clear the parameter
    st.query_params.clear()
    
# Check for rerun parameter in URL
params = st.query_params
if "rerun" in params:
    # Clear the rerun parameter
    st.query_params.clear()
    # Force reinitialization
    if "handler_initialized" in st.session_state:
        st.session_state.handler_initialized = False
    if "chat_handler" in st.session_state:
        del st.session_state.chat_handler
    st.rerun()

# If force_rerun is set, reset the chat handler and force a rerun
if st.session_state.force_rerun:
    if 'chat_handler' in st.session_state:
        print("Force rerun requested. Reinitializing chat handler.")
        del st.session_state.chat_handler
        st.session_state.handler_initialized = False
        st.session_state.force_rerun = False
        st.rerun()

# Load styles and scripts
StyleLoader.load_css([
    config.get_config()["folder_css"],
    "streamlit_app/static/styles.css"  # Load external CSS
])
StyleLoader.load_js([
    config.get_config()["folder_js"],
    "streamlit_app/static/scripts.js"  # Load external JS
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
        print("Chat handler is now ready! Setting handler_initialized to True")
        st.session_state.handler_initialized = True
        # We'll use JavaScript to reload instead of st.rerun()
        return True
    
    # Add debug information
    print(f"Checking initialization status: is_ready={chat_handler.is_ready}, handler_initialized={st.session_state.handler_initialized}")
    
    return False

# Initialize chat handler (this won't block now)
if 'chat_handler' not in st.session_state:
    print("Creating new ChatHandler instance")
    st.session_state.chat_handler = ChatHandler()
    
# Check if we're just switching chats - skip reinitialization in that case
if "switching_chat" in st.session_state and st.session_state.switching_chat:
    print("Switching chats - skipping reinitialization of chat components")
    st.session_state.switching_chat = False  # Reset the flag
else:
    # Normal initialization check for new sessions
    check_initialization_status()

# Add a periodic status checker that runs every few seconds
if not st.session_state.handler_initialized and not ("switching_chat" in st.session_state and st.session_state.switching_chat):
    is_ready = check_initialization_status()
    if is_ready:
        print("Handler is ready, forcing rerun")
        st.rerun()

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

# Only show header and refresh buttons if not switching chats
# This prevents unnecessary re-rendering when just viewing chat history
if not ("switching_chat" in st.session_state and st.session_state.switching_chat):
    # Main app header with improved styling
    st.markdown(
        """
        <div class="main-header">
            <h1>MNT Team Chatbot</h1>
            <p>Ask questions about your data and get intelligent responses</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
sidebar.render()

# Display initialization status with better UI
chat_handler = st.session_state.chat_handler

# Show initialization status or refresh button based on state
if not chat_handler.is_ready:
    # Check if there was an initialization error
    error_message = ""
    if hasattr(chat_handler, 'initialization_error'):
        error_message = f"""
        <p class="error-message">
            Error during initialization: {chat_handler.initialization_error}
        </p>
        """
    
    # Only show the refresh buttons and loading animation if not switching chats
    if not ("switching_chat" in st.session_state and st.session_state.switching_chat):
        # Also add a native Streamlit button as a backup
        if st.button("🔄 Reinitialize Chatbot", type="primary"):
            # Force reinitialization
            if "handler_initialized" in st.session_state:
                st.session_state.handler_initialized = False
            if "chat_handler" in st.session_state:
                del st.session_state.chat_handler
            st.rerun()
    
    # Create loading message with attractive animation
    if not ("switching_chat" in st.session_state and st.session_state.switching_chat):
        st.markdown(
            f"""
            <div class="loading-animation">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
            <p class="loading-message">
                The chatbot is initializing. You can browse the interface but chat will be available shortly...
            </p>
            {error_message}
            <script>
            // Call the initialization checker function from external JS
            document.addEventListener('DOMContentLoaded', function() {{
                if (typeof initializationChecker === 'function') {{
                    initializationChecker();
                }}
            }});
            </script>
            """, 
            unsafe_allow_html=True
        )
else:
    # Only show refresh button if manually needed and not switching chats
    if not ("switching_chat" in st.session_state and st.session_state.switching_chat):
        # Remove the HTML button and keep only the native Streamlit button
        if st.button("🔄 Reinitialize Chatbot", type="primary"):
            # Force reinitialization
            if "handler_initialized" in st.session_state:
                st.session_state.handler_initialized = False
            if "chat_handler" in st.session_state:
                del st.session_state.chat_handler
            st.rerun()

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
            st.markdown(
                f"""
                <div class="user-message">
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

# Reset the switching_chat flag after displaying messages
if "switching_chat" in st.session_state and st.session_state.switching_chat:
    st.session_state.switching_chat = False

# Chat input - disable if not ready
input_placeholder = "Type your message here..."
if not chat_handler.is_ready:
    input_placeholder = "Please wait while the system initializes..."

# Process user input
if prompt := st.chat_input(input_placeholder, disabled=not chat_handler.is_ready):
    # Add debug information
    print(f"Received user input: {prompt}")
    print(f"Chat handler status: is_ready={chat_handler.is_ready}, handler_initialized={st.session_state.handler_initialized}")
    
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
                
                # Handle None or empty responses
                # if not response_content:
                #     response_content = "I'm sorry, I couldn't generate a response at this time. Please try again later."
                
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