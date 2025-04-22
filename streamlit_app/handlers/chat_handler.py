# import necessary library
import os
import sys
import tiktoken
import threading
import streamlit as st
from typing import  Any
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.retrievers import EnsembleRetriever
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")

# import external file
from streamlit_app.utils.config import Config
from streamlit_app.utils.logger import logger
from streamlit_app.handlers.chat_modules.vector_db_handler import VectorDBHandler
from streamlit_app.handlers.chat_modules.retriever_handler import RetrieverHandler
from streamlit_app.handlers.chat_modules.response_formatter import ResponseFormatter

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
    """
    Initlize Chat Handler instance to handle chatbot

    Args:
        embedding model: to convert text into vector database
        vectordb: FAISS vectordb
        llm: model AI
        _is_initialized: to check chat handler is initlized
        _initialization_lock: check chat bar is still lock
    """
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

        # Create helpers object
        self.vector_db_handler = VectorDBHandler(model_name_vectordb, cache_folder)
        self.retriever_handler = RetrieverHandler()
        self.response_formatter = ResponseFormatter()
        
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
                            ChatHandler._embeddings = self.vector_db_handler.load_embeddings()
                            logger.info("Embeddings loaded successfully!")
                        except Exception as e:
                            logger.error(f"Error loading embeddings: {e}")
                            raise
                    
                    # Download and load vector store from S3
                    if ChatHandler._vector_db is None:
                        logger.info("Downloading vector database from S3...")
                        
                        # Download vector database files from S3
                        ChatHandler._vector_db = self.vector_db_handler.download_and_load_vector_db()
                        if ChatHandler._vector_db is None:
                            logger.warning("WARNING: Vector database is None after downloading!")
                            logger.warning("Continuing without vector database - chat functionality will be limited")
                        else:
                            logger.info("Vector database downloaded successfully!")
                    
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
                    self.retriever = self.retriever_handler.set_up_retriever(self.vector_db)
                    logger.info("Retriever setup complete!")
                
                logger.info(f"Setting is_ready to True. vector_db: {self.vector_db is not None}, retriever: {self.retriever is not None}")
                self.is_ready = True
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            # Don't set is_ready to True when there's an error
            self.is_ready = False
            # Add more detailed error information
            self.initialization_error = str(e)

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
            template = """You're assistant about job dataset from Linkedin, if user ask question not in job data, just answer "I don't know

            Instruction:
            - pick one of the most meaningful information from details in this job
            - show 5 results, each with: company_name, url, job_title, job_location, job_role
            - show best match first, then rest
            - if possible, let make it better format

            {context}

            Question: {question}
            Answer:"""

            PROMPT = PromptTemplate(
                template=template, 
                input_variables=["context", "question"]
            )

            # Set up a more detailed chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                # return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT},
                verbose=True  # Add this to see processing details
            )

            # Run query with full response
            logger.info("Running hybrid search query...")
            try:
                result = qa_chain.invoke({"query": query})
                logger.info(f"Successfully retrieved answer with {len(result.get('source_documents', []))} source documents")
                # Log the source documents for debugging
                if "source_documents" in result and result["source_documents"]:
                    for i, doc in enumerate(result["source_documents"][:2]):  # Show first 2 docs
                        preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                        print(f"Source document {i+1}: {preview}")
                # format_result = self.response_formatter.format_response(result["result"])
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
    
    def stream_response(self, response: str, placeholder: Any) -> None:
        """
        Stream the response with typing effect and proper Markdown formatting
        
        Args:
            response (str): Response text to stream
            placeholder: Streamlit placeholder for displaying response
        """
        try:
            self.response_formatter.stream_response(response, placeholder)
        except Exception as e:
            print(f"Error in stream_response: {str(e)}")
            placeholder.markdown(f"Error displaying response: {str(e)}")
            # Try to display the full response at once
            try:
                if response:
                    placeholder.markdown(response)
            except:
                pass