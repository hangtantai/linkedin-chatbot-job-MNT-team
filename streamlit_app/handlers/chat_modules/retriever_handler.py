# Check if running on Streamlit Cloud
import os
import sys
import pickle
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
from streamlit_app.utils.config import Config
from streamlit_app.utils.logger import logger
from langchain.retrievers import EnsembleRetriever

# Variables
config = Config().get_config()
k_document = config["k_document"]
bm25_file = config["bm25_file"]
weight_semantic = config["weight_semantic"]
name_algo = config["algorithm_search_keyword"]
class RetrieverHandler:
    """
    Handles the setup of retriever for the program
    """
    def __init__(self):
        """
        initliaze the retriever handler
        Args:
            None
        """
        pass
    
    def set_up_retriever(self, vector_db):
        """
        To set up retriever for the program
        Args:
            vector_db: Vector database
        Returns:
            retriever: Retriever object: ensemble retriever: BM25 and FAISS semantic search
        """
        vector_retriever = vector_db.as_retriever(search_kwargs={"k": k_document}) 
        retriever = vector_retriever
        
        # Load hybrid retriever if BM25 file exists
        try:
            vector_db_path = config["vector_db_path"]
            bm25_path = os.path.join(os.path.dirname(vector_db_path), bm25_file)
            
            if os.path.exists(bm25_path):
                logger.info(f"Loading {name_algo} retriever from {bm25_path}")
                with open(bm25_path, "rb") as f:
                    bm25_retriever = pickle.load(f)
                    
                # Create ensemble retriever (hybrid search)
                retriever = EnsembleRetriever(
                    retrievers=[bm25_retriever, vector_retriever],
                    weights=[1 - weight_semantic, weight_semantic]  # Weight semantic search higher
                )
                logger.info(f"Hybrid retriever ({name_algo} + Vector) setup complete!")
            else:
                logger.info(f"{name_algo} retriever not found. Using vector retriever only.")
        except Exception as e:
            logger.error(f"Error setting up {name_algo} retriever: {e}, falling back to vector retriever")
        
        return retriever
