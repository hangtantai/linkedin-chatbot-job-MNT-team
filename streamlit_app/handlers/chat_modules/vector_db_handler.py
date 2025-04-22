# Check if running on Streamlit Cloud
import os
import sys
import boto3
import os
import traceback
from typing import Optional
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
from streamlit_app.utils.config import Config
from streamlit_app.utils.logger import logger
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


config = Config().get_config()

class VectorDBHandler:
    """
    Handles operations related to vector database
    - Loading embeddings
    - Downloading and loading vector database from s3
    - Loading FAISS vector store
    """

    def __init__(self, model_name: str, cache_folder: str):
        """
        Initialize the vector database handler
        Args:
            model_name (str): The name of the model to use for embeddings
            cache_folder (str): The folder to cache the embeddings
        """
        self.model_name = model_name
        self.cache_folder = cache_folder

    def load_embeddings(self) -> HuggingFaceEmbeddings:
        """
        Load embeddings from HuggingFace
        Returns:
            HuggingFaceEmbeddings: The loaded embeddings
        """
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                cache_folder=self.cache_folder
            )
            return embeddings
        except:
            logger.error("Error loading embeddings")
            raise
    
    def download_and_load_vector_db(self) -> None:
        """
        Download vector database from S3
        """
        try:
            vector_db_path = config["vector_db_path"]
            bucket_name = config["bucket_vectordb"]
            s3_prefix = config["prefix_vectodb"]
            
            # Create directory if it doesn't exist
            os.makedirs(vector_db_path, exist_ok=True)
            
            # Download FAISS files from S3
            try:
                s3_client = boto3.client("s3")
                logger.info(f"Downloading files from {bucket_name}/{s3_prefix} to {vector_db_path}")
                
                # List objects in the prefix
                response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        s3_key = obj['Key']
                        # Extract relative path from the s3_key
                        rel_path = os.path.relpath(s3_key, s3_prefix)
                        local_path = os.path.join(vector_db_path, rel_path)
                        
                        # Create subdirectories if needed
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        
                        logger.info(f"Downloading {s3_key} to {local_path}")
                        s3_client.download_file(bucket_name, s3_key, local_path)
                    
                    logger.info("Vector database files downloaded successfully!")
                    
                    # Also download BM25 retriever
                    try:
                        bm25_path = os.path.join(os.path.dirname(vector_db_path), config["bm25_file"])
                        s3_client.download_file(bucket_name, config["dir_bm25"], bm25_path)
                        logger.info(f"Downloaded BM25 retriever to {bm25_path}")
                    except Exception as e:
                        logger.warning(f"Could not download BM25 retriever: {e}")
                else:
                    logger.error(f"No files found in S3 at {bucket_name}/{s3_prefix}")
                    
            except Exception as e:
                logger.error(f"Error downloading vector database from S3: {e}")
                # We'll continue and try to load from local path if files exist
            
            # Now load the vector database using the local files
            logger.info("Loading vector database...")
            return self._load_vector_store()
        except Exception as e:
            logger.error(f"Error in download_and_load_vector_db: {e}")
            return None
    
    def _load_vector_store(self) -> Optional[FAISS]:
        """
        Initialize and load FAISS vector store from local path
        
        Returns:
            Optional[FAISS]: The loaded FAISS vector store, or None if loading fails
        """
        try:
            vector_db_path = config["vector_db_path"]
            
            # Now check if the required files are present
            index_faiss_path = os.path.join(vector_db_path, "index.faiss")
            index_pkl_path = os.path.join(vector_db_path, "index.pkl")

            if not os.path.exists(index_faiss_path) or not os.path.exists(index_pkl_path):
                logger.error(f"Required vector database files not found: {index_faiss_path}, {index_pkl_path}")
                return None
            
            logger.info(f"Loading FAISS index from {vector_db_path}...")

            # Load embeddings if not already loaded
            embeddings = self.load_embeddings()
            
            vector_db = FAISS.load_local(
                folder_path=vector_db_path,
                embeddings=embeddings,
                allow_dangerous_deserialization=True
            )
            return vector_db
        except Exception as e:
            logger.error(f"Error loading FAISS: {e}")
            traceback.print_exc()
            return None

