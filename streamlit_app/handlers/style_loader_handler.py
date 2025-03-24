# import necessary library
import streamlit as st
from typing import Union, Dict, List
import os
import sys

# if using on Streamlit CLoud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

# import external file
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