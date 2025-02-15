import os 
import time
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient 
from bson.objectid import ObjectId
from langchain_groq import ChatGroq
load_dotenv()

# MongoDB setup
mongo_client = MongoClient(os.environ['MONGO_URI'])
db = mongo_client['chatbot']
chat_collection = db['chat_history']

# initialize variables
time_sleep = .02
max_word = 15

# Initialize session states
if "llm" not in st.session_state:
    st.session_state.llm = ChatGroq(temperature=0, model_name="llama3-70b-8192")

if "model" not in st.session_state:
    st.session_state.model = "llama3-70b-8192"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

# Function to create new chat
def create_new_chat() -> None:
    """"
    Create a new chat and set it as the selected chat.
    """
    st.session_state.chat_id = str(ObjectId())
    st.session_state.messages = []
    chat_collection.insert_one({
        "_id": ObjectId(st.session_state.chat_id), 
        "messages": [],
        "title": "New Chat" # default title
    })
    if "selected_chat" in st.session_state:
        del st.session_state.selected_chat
    st.rerun()

# Function to switch chat
def switch_chat(chat_id: str) -> None:
    """
    Switch to a different chat by setting the chat_id and loading messages.

    Args:
        chat_id (str): The ID of the chat to switch to.
    """
    chat = chat_collection.find_one({"_id": chat_id})
    # check if chat exists
    if chat:
        st.session_state.messages = chat.get("messages", [])
        st.session_state.chat_id = str(chat_id)
        if "selected_chat" not in st.session_state:
            st.session_state.selected_chat = str(chat_id)
        st.rerun()

# Function to get chat title
def get_chat_title(chat: dict) -> str:
    """
    Get chat title from first message or return default title.
    
    Args:
        chat (dict): The chat dictionary.
    """
    messages = chat.get("messages", [])
    if messages:
        # Get first message content
        first_message = messages[0].get("content", "")
        # Split into words and take first 15
        words = first_message.split()[:15]
        # Join words and add ellipsis if truncated
        title = " ".join(words)
        if len(words) < len(first_message.split()):
            title += "..."
        return title
    
    # If no messages or custom title, return default
    return chat.get("title", "New Chat")

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

# Helper function to escape special characters
def escape_for_js(text: str) -> str:
    """
    Escape special characters for JavaScript string.
    
    Args:
        text (str): The text to escape.
    """
    return text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')

# Main app title
st.title("Chatbot MNT team")

# Sidebar
with st.sidebar:
    st.title("Chat History")
    
    # New chat button
    if st.button("➕ New Chat", key="new_chat_btn", type="primary"):
        create_new_chat()
    
    st.markdown("---")

    # check if sidebar needs to be updated after renaming
    if "sidebar_updated" in st.session_state:
        del st.session_state.sidebar_updated
        st.rerun()
    
    # Display chat history
    # Sort by newest first
    for idx, chat in enumerate(chat_collection.find().sort("_id", -1)):  
        chat_id = chat.get("_id")
        messages = chat.get("messages", [])
        
        title = get_chat_title(chat)

        # Create a container for each chat item
        chat_container = st.container()
        
        # Use columns for chat title and options
        with chat_container:
            col1, col2 = st.columns([7, 3])
            
            # Chat title button
            with col1:
                button_key = f"chat_button_{idx}_{str(chat_id)}"
                if st.button(f"💬 {title}", key=button_key):
                    st.session_state.chat_id = str(chat_id)
                    switch_chat(chat_id)
            
            # Options dropdown
            with col2:
                option = st.selectbox(
                    "Chat options",  
                    ["⋮", "Rename", "Delete"],
                    key=f"options_{idx}_{str(chat_id)}",
                    label_visibility="collapsed"
                )
                
                if option == "Delete":
                    if chat_id == st.session_state.chat_id:
                        create_new_chat()
                    chat_collection.delete_one({"_id": ObjectId(chat_id)})
                    st.rerun()
                
                elif option == "Rename":
                    st.session_state[f"show_rename_{chat_id}"] = True
                    show_rename(chat_id, title, chat_collection)
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
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Check if this is a new chat
    if st.session_state.chat_id is None:
        # Create new chat only when first message is sent
        new_chat_id = ObjectId()
        st.session_state.chat_id = str(new_chat_id)
        chat_collection.insert_one({
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
            chat_collection.update_one(
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



# Custom CSS for styling the copy button
st.markdown("""
<style>
    /* ... existing CSS ... */

    /* Copy button styling */
    .message-container {
        position: relative;
    }
    
    .copy-button {
        position: absolute;
        top: 8px;
        right: 8px;
        padding: 4px 8px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
        display: none;
        transition: all 0.2s;
    }
    
    .message-container:hover .copy-button {
        display: block;
    }
    
    .copy-button:hover {
        background: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# Add JavaScript for copy functionality
st.markdown("""
<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Optional: Show feedback that text was copied
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    });
}
</script>
""", unsafe_allow_html=True)


# Custom CSS for styling for chat history buttons
st.markdown("""
<style>
    /* Chat history buttons */
    .stButton button {
        width: 100%;
        border: none;
        outline: none;
        background-color: #f0f0f0;
        padding: 10px;
        margin: 5px 0;
        text-align: right;
        box-shadow: none;
        cursor: pointer;
        color: black;
        display: flex; 
        justify-content: flex-start; 
        align-items: center;
    }
    .stButton button:hover {
        background-color:#e0e0e0;
    }
    
    /* Main chat container */
    .main {
        max-width: 800px;
        margin: auto;
    }
    
    /* Message containers */
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Chat input */
    .stChatInputContainer {
        padding: 1rem;
        border-top: 1px solid #e0e0e0;
    }
            
    /* Dropdown styling */
    .stSelectbox {
        margin-top: 7px;
    }
            
    /* Container of the selectbox */
    .stSelectbox > div > div {
        padding: 2px;
        min-height: 35px;
        border: none;
        background: transparent;
    }
            
    /* Hide dropdown arrow */
    .stSelectbox > div > div > div:last-child {
        display: none;
    }
            
    /* Remove hover background */
    .stSelectbox > div > div:hover {
        background: transparent;
    }
            
    /* Remove padding from columns */
    [data-testid="column"] {
        padding: 0 !important;
    }
            
    /* Align text input with buttons */
    .stTextInput input {
        padding: 5px 10px;
        margin-top: 5px;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# sample message
# font
# icon chat
# logo