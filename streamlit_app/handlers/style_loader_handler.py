import streamlit as st
from typing import Union, Dict, List
import os
import sys
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
from streamlit_app.helpers.processing_text import escape_for_js
class StyleLoader:
    @staticmethod
    def load_css(css_files: list):
        """Load multiple CSS files"""
        css_content = ""
        for css_file in css_files:
            with open(css_file, 'r') as f:
                css_content += f.read() + "\n"
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        
    @staticmethod
    def load_js(js_files: Union[Dict[str, str], List[str]]) -> None:
        """Load JavaScript files into Streamlit"""
        if isinstance(js_files, dict):
            for _, file_path in js_files.items():
                with open(file_path, 'r') as file:
                    js_content = file.read()
                    st.markdown(
                        f"<script>{js_content}</script>",
                        unsafe_allow_html=True
                    )
        elif isinstance(js_files, list):
            for file_path in js_files:
                with open(file_path, 'r') as file:
                    js_content = file.read()
                    st.markdown(
                        f"<script>{js_content}</script>",
                        unsafe_allow_html=True
                    )


class MessageDisplay:
    @staticmethod
    def render_message(message: dict) -> None:
        """Render a single chat message with copy functionality"""
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

    @staticmethod
    def render_messages(messages: list) -> None:
        """Render all chat messages"""
        for message in messages:
            MessageDisplay.render_message(message)