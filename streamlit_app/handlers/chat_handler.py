from langchain_groq import ChatGroq
import streamlit as st
import time
from typing import List, Dict, Any, Optional
import os
import sys
import tiktoken
from langchain.chains import RetrievalQA
import threading
from langchain.retrievers import EnsembleRetriever
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

from streamlit_app.utils.config import Config
from streamlit_app.utils.utils_chat import check_token_limit
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain_chroma import Chroma
import pickle
from langchain.prompts import PromptTemplate
from streamlit_app.utils.logger import logger
# Initialize configuration
config = Config()
api_key = st.secrets["GROQ_API_KEY"]

# Initialize configuration
config.initialize_session_states()

# Variables
time_sleep_var = config.get_config()["time_sleep"]
temperature_var = config.get_config()["temperature"]
model_name_var = config.get_config()["model_name"]
max_tokens_var = int(config.get_config()["max_tokens"])
assistant_message_row = int(config.get_config()["assistant_message_row"])
defaul_model_token = config.get_config()["defaul_model_token"]
model_name_vectordb = config.get_config()["model_name_vectordb"] 
cache_folder = config.get_config()["cache_folder"] 
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
class ChatHandler:
    _embeddings = None
    _vector_db = None
    _is_initialized = False
    _initialization_lock = threading.Lock()

    def __init__(self, model_name: str = model_name_var, temperature: int = temperature_var):
        self.llm = ChatGroq(api_key=api_key, model_name=model_name, temperature=temperature, max_tokens=max_tokens_var)
        self.time_sleep = time_sleep_var
        self.max_tokens = max_tokens_var
        self.encoding = tiktoken.get_encoding(defaul_model_token)

        # Set initialization flags
        self.is_ready = False
        
        # Start background initialization
        threading.Thread(target=self._initialize_in_background, daemon=True).start()

    def _initialize_in_background(self):
        """Initialize embeddings and vector database in a background thread"""
        try:
            with ChatHandler._initialization_lock:
                if not ChatHandler._is_initialized:
                    # Load embeddings
                    if ChatHandler._embeddings is None:
                        logger.info("Loading embeddings model...")
                        try:
                            ChatHandler._embeddings = HuggingFaceEmbeddings(
                                model_name=model_name_vectordb,
                                cache_folder=cache_folder
                            )
                            logger.info("Embeddings loaded successfully!")
                        except Exception as e:
                            logger.error(f"Error loading embeddings: {e}")
                            raise
                    
                    # Load vector store
                    if ChatHandler._vector_db is None:
                        logger.info("Loading vector database...")
                        ChatHandler._vector_db = self._load_vector_store()
                        if ChatHandler._vector_db is None:
                            logger.warning("WARNING: Vector database is None after loading!")
                            # If vector database is None, we'll still mark as initialized but log a warning
                            logger.warning("Continuing without vector database - chat functionality will be limited")
                        else:
                            logger.info("Vector database loaded successfully!")
                    
                    ChatHandler._is_initialized = True
                    logger.info("ChatHandler initialization complete!")
                
                # Set instance variables
                self.embeddings = ChatHandler._embeddings
                self.vector_db = ChatHandler._vector_db
                
                # Always set is_ready to True even if vector_db is None
                # This allows the application to proceed even with limited functionality
                if self.vector_db is None:
                    logger.warning("WARNING: self.vector_db is None! Chat will have limited functionality.")
                    self.retriever = None
                else:
                    logger.info("Setting up retriever...")
                    # Set up vector retriever
                    vector_retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
                    
                    # Load hybrid retriever if BM25 file exists
                    try:
                        vector_db_path = config.get_config()["vector_db_path"]
                        bm25_path = os.path.join(os.path.dirname(vector_db_path), "bm25.pkl")
                        
                        if os.path.exists(bm25_path):
                            logger.info(f"Loading BM25 retriever from {bm25_path}")
                            with open(bm25_path, "rb") as f:
                                bm25_retriever = pickle.load(f)
                                
                            # Create ensemble retriever (hybrid search)
                            self.retriever = EnsembleRetriever(
                                retrievers=[bm25_retriever, vector_retriever],
                                weights=[0.3, 0.7]  # Weight semantic search higher
                            )
                            logger.info("Hybrid retriever (BM25 + Vector) setup complete!")
                        else:
                            logger.info("BM25 retriever not found. Using vector retriever only.")
                            self.retriever = vector_retriever
                    except Exception as e:
                        logger.error(f"Error setting up BM25 retriever: {e}, falling back to vector retriever")
                        self.retriever = vector_retriever
                    logger.info("Retriever setup complete!")
                
                logger.info(f"Setting is_ready to True. vector_db: {self.vector_db is not None}, retriever: {self.retriever is not None}")
                self.is_ready = True
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            # Don't set is_ready to True when there's an error
            self.is_ready = False
            # Add more detailed error information
            self.initialization_error = str(e)

    def _load_vector_store(self) -> Optional[FAISS]:
        """Initialize and load FAISS vector store"""
        try:
            vector_db_path = config.get_config()["vector_db_path"]
            index_faiss_path = os.path.join(vector_db_path, "index.faiss")
            index_pkl_path = os.path.join(vector_db_path, "index.pkl")

            # check 2 files exist
            if not os.path.exists(index_faiss_path) or not os.path.exists(index_pkl_path):
                logger.error("Vector database files not found! Please generate them first.")
                return None
            
            logger.info(f"Loading FAISS index from {vector_db_path}...")

            vector_db = FAISS.load_local(
                folder_path=vector_db_path,
                embeddings=self._embeddings,
                allow_dangerous_deserialization=True
            )
            return vector_db
        except Exception as e:
            logger.error(f"Error loading FAISS: {e}")
            return None

    # def _load_vector_store(self) -> Optional[Chroma]:
    #     """Initialize and load Chroma vector store"""
    #     try:
    #         vector_db_path = config.get_config()["vector_db_path"]

    #         # Check if directory exists
    #         if not os.path.exists(vector_db_path) or not os.path.isdir(vector_db_path):
    #             logger.error(f"Chroma directory not found at {vector_db_path}!")
    #             return None
            
    #         # Look for Chroma files
    #         chroma_files = [f for f in os.listdir(vector_db_path) if f.endswith('.sqlite3') or f.endswith('.parquet')]
    #         if not chroma_files:
    #             logger.error(f"No Chroma database files found in {vector_db_path}. Please generate them first.")
    #             return None
            
    #         logger.info(f"Loading Chroma from {vector_db_path}...")
            
    #         # Load Chroma database
    #         vector_db = Chroma(
    #             persist_directory=vector_db_path,
    #             embedding_function=self._embeddings
    #         )
            
    #         return vector_db
    #     except Exception as e:
    #         logger.error(f"Error loading Chroma: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         return None
        
    def retrieve_qa(self, query) -> str:
        """
        Use the retriever to run a question-answering chain based on retrieved documents.

        Args:
            query: The user's query to answer

        Returns:
            str: The response generated by the LLM.
        """
        try:
            if not self.vector_db or not self.retriever:
                logger.warning("Vector database or retriever not available, using direct LLM response")
                # If vector database is not available, use the LLM directly
                response = self.llm.invoke(query)
                return response.content
            
            # Log retriever type for debugging
            if isinstance(self.retriever, EnsembleRetriever):
                logger.info("Using hybrid retriever (BM25 + Vector)")
            else:
                logger.warning("Using standard vector retriever")
                
           # Create a custom prompt template that emphasizes using context
            template = """Answer the question based only on the following context:

            {context}

            Question: {question}
            Answer: """

            PROMPT = PromptTemplate(
                template=template, 
                input_variables=["context", "question"]
            )

            # Set up a more detailed chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT},
                verbose=True  # Add this to see processing details
            )

            # Run query with full response
            logger.info("Running hybrid search query...")
            # result = qa_chain.invoke({"query": query})
            # return result["result"]
            try:
                result = qa_chain.invoke({"query": query})
                logger.info(f"Successfully retrieved answer with {len(result.get('source_documents', []))} source documents")
                # result = qa_chain.invoke({"query": query})
                # Log the source documents for debugging
                if "source_documents" in result and result["source_documents"]:
                    for i, doc in enumerate(result["source_documents"][:2]):  # Show first 2 docs
                        preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                        print(f"Source document {i+1}: {preview}")
                logger.info("QNA runs successfully")
                return result["result"]
            except KeyError:
                logger.warning("KeyError in qa_chain.invoke result - checking alternative keys")
                # Some versions of LangChain use different keys
                if "answer" in result:
                    return result["answer"]
                elif "output_text" in result:
                    return result["output_text"]
                else:
                    logger.warning(f"Available keys in result: {list(result.keys())}")
                    raise ValueError("Could not find result key in QA response")
                    
        except Exception as e:
            logger.error(f"Error in retrieve_qa: {str(e)}")
            st.error(f"Error in retrieve_qa: {str(e)}")
            
    
    def filter_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filter messages from chat history, placing user messages at the end
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries
        
        Returns:
            List[Dict[str, str]]: Filtered messages with user messages at the end
        """
        try:
            # Get assistant messages first
            result_filter = []
            assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]
            user_messages = [msg for msg in messages if msg["role"] == "user"]
            
            # Add last N assistant messages if they exist
            if assistant_messages:
                result_filter.extend(assistant_messages[-assistant_message_row:])
            
            # Add user messages at the end
            result_filter.extend(user_messages)
            
            return result_filter
        except Exception as e:
            st.error(f"Error filtering messages: {str(e)}")
            return []
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using the chat model
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'
        
        Returns:
            str: Generated response
        """
        try:
            if not check_token_limit(max_tokens_var, self.encoding, messages):
                st.error(f"Message length exceeds token limit of {self.max_tokens}")
                return None
            
            response = self.llm.invoke(
                input=messages,
                max_tokens=self.max_tokens
            )
            return response.content
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None
    
    def stream_response(self, response: str, placeholder: Any) -> None:
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
            
            import re
            
            def process_markdown(text):
                """Process markdown syntax to HTML for better rendering"""
                # Bold text
                text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
                
                # Italic text 
                text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
                
                # Headers
                text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
                text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
                text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
                
                # Numbered lists
                text = re.sub(r'^(\d+)\. (.*?)$', r'<ol start="\1"><li>\2</li></ol>', text, flags=re.MULTILINE)
                
                # Bullet lists
                text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
                
                # Consolidate consecutive list items
                text = re.sub(r'<\/li><\/ol>\s*<ol start="\d+"><li>', r'</li><li>', text)
                text = re.sub(r'<\/li>\s*<li>', r'</li><li>', text)
                
                # Wrap bullet lists in <ul> tags
                parts = text.split('<li>')
                result = parts[0]
                in_list = False
                
                for part in parts[1:]:
                    if not in_list:
                        result += '<ul><li>' + part
                        in_list = True
                    else:
                        if '</li>' in part and not re.search(r'<li>.*?</li>', part):
                            result += '</ul>' + part
                            in_list = False
                        else:
                            result += '<li>' + part
                
                # Code blocks
                text = result
                text = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', text, flags=re.DOTALL)
                
                # Inline code
                text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
                
                return text
                    
            full_response = ""
            # Stream by words for smoother effect
            words = response.split()
            for i, word in enumerate(words):
                full_response += word + " "
                time.sleep(self.time_sleep)
                
                # Apply markdown processing
                formatted_html = process_markdown(full_response)
                
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
                    .markdown-content ul, .markdown-content ol {{
                        margin-left: 1.5rem;
                        margin-bottom: 1rem;
                        padding-left: 1rem;
                    }}
                    .markdown-content li {{
                        margin-bottom: 0.3rem;
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
            escaped_content = response.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r")
            formatted_html = process_markdown(full_response)
            
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
                .markdown-content ul, .markdown-content ol {{
                    margin-left: 1.5rem;
                    margin-bottom: 1rem;
                    padding-left: 1rem;
                }}
                .markdown-content li {{
                    margin-bottom: 0.3rem;
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
        except Exception as e:
            print(f"Error in stream_response: {str(e)}")
            placeholder.markdown(f"Error displaying response: {str(e)}")
            # Try to display the full response at once
            try:
                if response:
                    placeholder.markdown(response)
            except:
                pass