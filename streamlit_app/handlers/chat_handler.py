from langchain_groq import ChatGroq
import streamlit as st
import time
from typing import List, Dict, Any, Optional
import os
import sys
import tiktoken
from langchain.chains import RetrievalQA
import threading
# Retriever
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

from streamlit_app.utils.config import Config
from streamlit_app.utils.utils_chat import check_token_limit
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import pickle
from langchain.prompts import PromptTemplate
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
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

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
                        print("Loading embeddings model...")
                        try:
                            ChatHandler._embeddings = HuggingFaceEmbeddings(
                                model_name="sentence-transformers/all-MiniLM-L6-v2",
                                cache_folder="streamlit_app/models/vector_db/"
                            )
                            print("Embeddings loaded successfully!")
                        except Exception as e:
                            print(f"Error loading embeddings: {e}")
                            raise
                    
                    # Load vector store
                    if ChatHandler._vector_db is None:
                        print("Loading vector database...")
                        ChatHandler._vector_db = self._load_vector_store()
                        if ChatHandler._vector_db is None:
                            print("WARNING: Vector database is None after loading!")
                            # If vector database is None, we'll still mark as initialized but log a warning
                            print("Continuing without vector database - chat functionality will be limited")
                        else:
                            print("Vector database loaded successfully!")
                    
                    ChatHandler._is_initialized = True
                    print("ChatHandler initialization complete!")
                
                # Set instance variables
                self.embeddings = ChatHandler._embeddings
                self.vector_db = ChatHandler._vector_db
                
                # Always set is_ready to True even if vector_db is None
                # This allows the application to proceed even with limited functionality
                if self.vector_db is None:
                    print("WARNING: self.vector_db is None! Chat will have limited functionality.")
                    self.retriever = None
                else:
                    print("Setting up retriever...")
                    # Set up vector retriever
                    vector_retriever = self.vector_db.as_retriever(search_kwargs={"k": 5})
                    
                    # Load hybrid retriever if BM25 file exists
                    try:
                        vector_db_path = config.get_config()["vector_db_path"]
                        bm25_path = os.path.join(os.path.dirname(vector_db_path), "bm25.pkl")
                        
                        if os.path.exists(bm25_path):
                            print(f"Loading BM25 retriever from {bm25_path}")
                            with open(bm25_path, "rb") as f:
                                bm25_retriever = pickle.load(f)
                                
                            # Create ensemble retriever (hybrid search)
                            self.retriever = EnsembleRetriever(
                                retrievers=[bm25_retriever, vector_retriever],
                                weights=[0.3, 0.7]  # Weight semantic search higher
                            )
                            print("Hybrid retriever (BM25 + Vector) setup complete!")
                        else:
                            print("BM25 retriever not found. Using vector retriever only.")
                            self.retriever = vector_retriever
                    except Exception as e:
                        print(f"Error setting up BM25 retriever: {e}, falling back to vector retriever")
                        self.retriever = vector_retriever
                    print("Retriever setup complete!")
                
                print(f"Setting is_ready to True. vector_db: {self.vector_db is not None}, retriever: {self.retriever is not None}")
                self.is_ready = True
        except Exception as e:
            print(f"Error during initialization: {e}")
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
                print("Vector database files not found! Please generate them first.")
                return None
            
            print(f"Loading FAISS index from {vector_db_path}...")

            vector_db = FAISS.load_local(
                folder_path=vector_db_path,
                embeddings=self._embeddings,
                allow_dangerous_deserialization=True
            )
            return vector_db
        except Exception as e:
            print(f"Error loading FAISS: {e}")
            return None
        
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
                print("Vector database or retriever not available, using direct LLM response")
                # If vector database is not available, use the LLM directly
                response = self.llm.invoke(query)
                return response.content
            
            # Log retriever type for debugging
            if isinstance(self.retriever, EnsembleRetriever):
                print("Using hybrid retriever (BM25 + Vector)")
            else:
                print("Using standard vector retriever")
                
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
            print("Running hybrid search query...")
            # return result["result"]
            try:
                result = qa_chain.invoke({"query", query})
                print(f"Successfully retrieved answer with {len(result.get('source_documents', []))} source documents")
                result = qa_chain.invoke({"query": query})
                # Log the source documents for debugging
                if "source_documents" in result and result["source_documents"]:
                    for i, doc in enumerate(result["source_documents"][:2]):  # Show first 2 docs
                        preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                        print(f"Source document {i+1}: {preview}")
                
                return result["result"]
            except KeyError:
                print("KeyError in qa_chain.invoke result - checking alternative keys")
                # Some versions of LangChain use different keys
                if "answer" in result:
                    return result["answer"]
                elif "output_text" in result:
                    return result["output_text"]
                else:
                    print(f"Available keys in result: {list(result.keys())}")
                    raise ValueError("Could not find result key in QA response")
                    
        except Exception as e:
            print(f"Error in retrieve_qa: {str(e)}")
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
        Stream the response with typing effect
        
        Args:
            response (str): Response text to stream
            placeholder: Streamlit placeholder for displaying response
        """
        try:
            if not response:
                placeholder.markdown("No response generated.")
                return
                
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(self.time_sleep)
                # placeholder.markdown(full_response + "▌")
                # Since we can't properly escape the full response for JS during streaming
                # (it changes with each chunk), we'll omit the copy button during streaming
                # and it will be added when the final message is displayed
                placeholder.markdown(
                    f"""
                    <div class="message-container" style="position: relative; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; background-color: #f8f9fa; border-left: 4px solid #28a745; box-shadow: 0 2px 5px rgba(0,0,0,0.05); animation: fadeIn 0.5s;">
                        {full_response}
                    </div>
                    <style>
                    @keyframes fadeIn {{
                        from {{ opacity: 0; transform: translateY(10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
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
                    placeholder.markdown(
                        f"""
                        <div class="message-container" style="position: relative; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; background-color: #f8f9fa; border-left: 4px solid #28a745; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                            {response}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except:
                pass