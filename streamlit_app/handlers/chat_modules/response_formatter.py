import re
import time
from typing import Any
import os
import sys
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

from streamlit_app.utils.logger import logger
from streamlit_app.utils.config import Config
from streamlit_app.helpers.processing_text import escape_for_js

# Variables
config = Config().get_config()
time_sleep = config["time_sleep"]

class ResponseFormatter:
    """
    Handles formatting and streaming of responses with markdown processing
    and styling for better presentation in Streamlit.
    """
    
    def __init__(self, time_sleep: float = time_sleep):
        """
        Initialize the ResponseFormatter
        
        Args:
            time_sleep: Time to sleep between words when streaming response
        """
        self.time_sleep = time_sleep
    
    def stream_response(self, response: str, placeholder: Any):
        """
        Stream the response with typing effect and proper Markdown formatting
        
        Args:
            response (str): Response text to stream
            placeholder: Streamlit placeholder for displaying response
        """
        try:
            if not response:
                placeholder.markdown("No response generated.")
                return
            
            full_response = ""
            # Stream by words for smoother effect
            words = response.split()
            for i, word in enumerate(words):
                full_response += word + " "
                time.sleep(self.time_sleep)
                
                # Apply markdown processing
                formatted_html = self.process_markdown(full_response)
                
                # Use formatted HTML with proper styling
                placeholder.markdown(
                    f"""
                    <div class="markdown-content">
                        {formatted_html}<span class="cursor">▌</span>
                    </div>
                    <style>
                    @keyframes blink {{
                        0%, 100% {{ opacity: 1; }}
                        50% {{ opacity: 0; }}
                    }}
                    .cursor {{
                        animation: blink 1s infinite;
                    }}
                    .markdown-content {{
                        line-height: 1.6;
                    }}
                    .markdown-content h1 {{
                        font-size: 1.5rem;
                        font-weight: bold;
                        margin-top: 1rem;
                        margin-bottom: 0.5rem;
                        padding-bottom: 0.3rem;
                        border-bottom: 1px solid #e1e4e8;
                    }}
                    .markdown-content h2 {{
                        font-size: 1.3rem;
                        font-weight: bold;
                        margin-top: 1rem;
                        margin-bottom: 0.5rem;
                    }}
                    .markdown-content h3 {{
                        font-size: 1.1rem;
                        font-weight: bold;
                        margin-top: 1rem;
                        margin-bottom: 0.5rem;
                    }}
                    .markdown-content p {{
                        margin-bottom: 0.8rem;
                    }}
                    .markdown-content ul {{
                        list-style-type: disc;
                        padding-left: 1rem;
                        margin-top: 0.8rem;
                        margin-bottom: 0.8rem;
                    }}
                    .markdown-content ul li {{
                        display: list-item;
                        margin-bottom: 0.8rem;
                        padding-left: 0.5rem;
                    }}
                    .markdown-content ol {{
                        list-style-type: none;
                        counter-reset: item;
                        padding-left: 0;
                        margin-top: 0.8rem;
                        margin-bottom: 0.8rem;
                    }}
                    .markdown-content ol li {{
                        display: block;
                        margin-bottom: 0.8rem;
                        padding-left: 0.5rem;
                    }}
                    .markdown-content code {{
                        font-family: SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace;
                        background-color: rgba(175, 184, 193, 0.2);
                        padding: 0.2rem 0.4rem;
                        border-radius: 3px;
                        font-size: 85%;
                    }}
                    .markdown-content pre {{
                        background-color: #f6f8fa;
                        border-radius: 6px;
                        padding: 16px;
                        overflow: auto;
                        font-size: 85%;
                        line-height: 1.45;
                        margin-bottom: 1rem;
                    }}
                    .markdown-content pre code {{
                        background-color: transparent;
                        padding: 0;
                        margin: 0;
                        white-space: pre;
                        overflow-wrap: normal;
                        border: 0;
                    }}
                    .markdown-content strong {{
                        font-weight: bold;
                    }}
                    .markdown-content em {{
                        font-style: italic;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
            
            # Final display without cursor and with copy button
            escaped_content = escape_for_js(response)
            formatted_html = self.process_markdown(full_response)
            
            placeholder.markdown(
                f"""
                <div class="message-container">
                    <div class="markdown-content">
                        {formatted_html}
                    </div>
                    <button class="copy-button" onclick="copyToClipboard('{escaped_content}')">
                        📋 Copy
                    </button>
                </div>
                <style>
                .message-container {{
                    position: relative;
                    padding-right: 40px;
                }}
                .copy-button {{
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    background-color: #f1f3f4;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 12px;
                    cursor: pointer;
                    opacity: 0.7;
                    transition: opacity 0.2s;
                }}
                .copy-button:hover {{
                    opacity: 1;
                }}
                .markdown-content {{
                    line-height: 1.6;
                }}
                .markdown-content h1 {{
                    font-size: 1.5rem;
                    font-weight: bold;
                    margin-top: 1rem;
                    margin-bottom: 0.5rem;
                    padding-bottom: 0.3rem;
                    border-bottom: 1px solid #e1e4e8;
                }}
                .markdown-content h2 {{
                    font-size: 1.3rem;
                    font-weight: bold;
                    margin-top: 1rem;
                    margin-bottom: 0.5rem;
                }}
                .markdown-content h3 {{
                    font-size: 1.1rem;
                    font-weight: bold;
                    margin-top: 1rem;
                    margin-bottom: 0.5rem;
                }}
                .markdown-content p {{
                    margin-bottom: 0.8rem;
                }}
                .markdown-content ul {{
                    list-style-type: disc;
                    padding-left: 1rem;
                    margin-top: 0.8rem;
                    margin-bottom: 0.8rem;
                }}
                .markdown-content ul li {{
                    display: list-item;
                    margin-bottom: 0.8rem;
                    padding-left: 0.5rem;
                }}
                .markdown-content ol {{
                    list-style-type: none;
                    counter-reset: item;
                    padding-left: 0;
                    margin-top: 0.8rem;
                    margin-bottom: 0.8rem;
                }}
                .markdown-content ol li {{
                    display: block;
                    margin-bottom: 0.8rem;
                    padding-left: 0.5rem;
                }}
                .markdown-content code {{
                    font-family: SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace;
                    background-color: rgba(175, 184, 193, 0.2);
                    padding: 0.2rem 0.4rem;
                    border-radius: 3px;
                    font-size: 85%;
                }}
                .markdown-content pre {{
                    background-color: #f6f8fa;
                    border-radius: 6px;
                    padding: 16px;
                    overflow: auto;
                    font-size: 85%;
                    line-height: 1.45;
                    margin-bottom: 1rem;
                }}
                .markdown-content pre code {{
                    background-color: transparent;
                    padding: 0;
                    margin: 0;
                    white-space: pre;
                    overflow-wrap: normal;
                    border: 0;
                }}
                .markdown-content strong {{
                    font-weight: bold;
                }}
                .markdown-content em {{
                    font-style: italic;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            logger.info("Response formatted")
        except Exception as e:
            logger.error(f"Error in stream_response: {str(e)}")
            placeholder.markdown(f"Error displaying response: {str(e)}")
            # Try to display the full response at once
            try:
                if response:
                    placeholder.markdown(response)
            except:
                pass
    
    def process_markdown(self, text):
        """Process markdown syntax to HTML for better rendering"""
        colon_list_match = re.search(r'(.*?):\s*((?:\d+\.\s+[^0-9\.\n]+(?:\([^)]+\))?(?:\s+)?)+)', text, re.DOTALL)
        if colon_list_match:
            prefix = colon_list_match.group(1)
            list_text = colon_list_match.group(2)
            
            # Split the list portion by numbers
            parts = re.split(r'(\d+\.\s+)', list_text)
            if len(parts) > 2:  # At least one number detected
                # Build the list items
                num_parts = []
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        num_parts.append(parts[i] + parts[i+1].strip())
                
                # If we have multiple items, format as a proper list
                if len(num_parts) > 1:
                    # Replace with prefix followed by properly formatted list
                    text = prefix + ":\n\n" + "\n".join(num_parts)
        
        # Also check for general inline list patterns without a colon
        elif re.search(r'\d+\.\s+\w+.*\d+\.\s+\w+', text):
            # This might be an inline list, let's process it
            parts = re.split(r'(\d+\.\s+)', text)
            if len(parts) > 2:  # At least one number detected
                # Determine if this is likely a list by checking if multiple numbered items exist
                num_parts = []
                for i in range(1, len(parts), 2):
                    if i+1 < len(parts):
                        num_parts.append(parts[i] + parts[i+1].strip())
                
                # If we have multiple numbered items, convert to proper list format
                if len(num_parts) > 1:
                    # Replace the original text with properly formatted list items
                    text = "\n".join(num_parts)
        
        # Bold text
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Italic text 
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Headers
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Process numbered lists with a more robust approach
        # First identify consecutive numbered list items
        lines = text.split('\n')
        in_numbered_list = False
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if this is a numbered list item
            numbered_match = re.match(r'^(\d+)\. (.*?)$', line)
            
            if numbered_match:
                # If we're not already in a numbered list, start one
                if not in_numbered_list:
                    # Add spacing before the list if it follows a paragraph
                    if processed_lines and not processed_lines[-1].strip() == '':
                        processed_lines.append('<div style="margin-top: 0.5rem;"></div>')
                    processed_lines.append('<ol>')
                    in_numbered_list = True
                
                # Extract the number and content
                number = numbered_match.group(1)
                content = numbered_match.group(2)
                
                # Add the list item with bold number
                processed_lines.append(f'<li><strong>{number}.</strong> {content}</li>')
            else:
                # If we were in a numbered list, close it
                if in_numbered_list:
                    processed_lines.append('</ol>')
                    # Add spacing after the list if it's followed by text
                    if line.strip() != '':
                        processed_lines.append('<div style="margin-bottom: 0.5rem;"></div>')
                    in_numbered_list = False
                
                # Add the regular line
                processed_lines.append(line)
            
            i += 1
        
        # Close any open list
        if in_numbered_list:
            processed_lines.append('</ol>')
        
        # Join back to text
        text = '\n'.join(processed_lines)
        
        # Bullet lists with improved formatting
        bullet_pattern = r'^- (.*?)$'
        
        # Process bullet lists similar to numbered lists
        lines = text.split('\n')
        in_bullet_list = False
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            bullet_match = re.match(bullet_pattern, line)
            
            if bullet_match:
                # If we're not already in a bullet list, start one
                if not in_bullet_list:
                    # Add spacing before the list if it follows a paragraph
                    if processed_lines and not processed_lines[-1].strip() == '':
                        processed_lines.append('<div style="margin-top: 0.5rem;"></div>')
                    processed_lines.append('<ul>')
                    in_bullet_list = True
                
                # Add the bullet item
                content = bullet_match.group(1)
                processed_lines.append(f'<li>{content}</li>')
            else:
                # If we were in a bullet list, close it
                if in_bullet_list:
                    processed_lines.append('</ul>')
                    # Add spacing after the list if it's followed by text
                    if line.strip() != '':
                        processed_lines.append('<div style="margin-bottom: 0.5rem;"></div>')
                    in_bullet_list = False
                
                # Add the regular line
                processed_lines.append(line)
            
            i += 1
        
        # Close any open list
        if in_bullet_list:
            processed_lines.append('</ul>')
        
        # Join back to text
        text = '\n'.join(processed_lines)
        
        # Code blocks
        text = re.sub(r'``[(\w+)?\n(.*?)](cci:1://file:///c:/Users/Hang%20Tan%20Tai/Documents/personal_space/selenium/streamlit_app/handlers/chat_handler.py:51:4-61:84)``', r'<pre><code class="language-\1">\2</code></pre>', text, flags=re.DOTALL)
        
        # Inline code
        text = re.sub(r'[(.*?)](cci:1://file:///c:/Users/Hang%20Tan%20Tai/Documents/personal_space/selenium/streamlit_app/handlers/chat_handler.py:51:4-61:84)', r'<code>\1</code>', text)
        
        return text