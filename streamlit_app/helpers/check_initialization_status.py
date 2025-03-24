import streamlit as st
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