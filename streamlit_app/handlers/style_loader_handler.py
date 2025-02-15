import streamlit as st

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
    def load_js(js_files: list):
        """Load multiple JavaScript files"""
        js_content = ""
        for js_file in js_files:
            with open(js_file, 'r') as f:
                js_content += f.read() + "\n"
        st.markdown(f"<script>{js_content}</script>", unsafe_allow_html=True)