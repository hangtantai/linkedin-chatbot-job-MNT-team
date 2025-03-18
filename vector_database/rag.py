# Utilization
import os
import pandas as pd
from io import StringIO 
# Document and Splitter
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
# Vector Store
from langchain_community.vectorstores import FAISS
# QNA
from streamlit_app.utils.config import Config
# Hybrid Search components
from langchain_community.retrievers import BM25Retriever
import pickle
import boto3
import streamlit as st

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def load_documents(df: pd.DataFrame) -> list:
    """
    Convert data into Documents

    Args:
        Data frame: Data to be converted into documents

    Returns:
        Documents includes page content and metadata
    """
    # Convert into documents
    documents = [
        Document(
            page_content=f'''Job Title: {row["job_title"]}
            \nCompany Name: {row["company_name"]}
            \nJob Location: {row["job_location"]}
            \nLink to the job: {row["url"]}
            \nTime of the job that is posted in Linkedin: {row["job_time_posted"]}
            \nApplicants of Job that is applied: {row["job_applicants_applied"]}
            \nRole of the job: {row["job_role"]}
            \nDetails of the job: it include: qualification, requirement, beneficial and something like that: {row["job_details"]}''',
            metadata={
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "job_location": row["job_location"]
            },
        )
        for _, row in df.iterrows()
    ]
    return documents

def chunk_text(documents: list, chunk_size: int = 1000, chunk_overlap: int = 100) -> list:
    """
    Split large documents into smaller chunks for better processing and embedding.

    Args:
        documents (list): List of langchain Document objects.
        chunk_size (int): The maximum size of each text chunk.
        chunk_overlap (int): The number of characters that overlap between chunks to ensure context.

    Returns:
        list: A list of chunked documents (smaller texts).
    """
    # Use RecursiveCharacterTextSplitter to chunk large texts
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        add_start_index=True
    )
    split_docs = splitter.split_documents(documents)
    return split_docs

def embed_and_store(doc_chunks: list, db_path: str, device: str = "cpu", batch_size: int = 32, normal_embeddings: bool = True):
    """
    Embed the document chunks and store them in a vector database (FAISS).

    Args:
        doc_chunks (list): The chunked documents to be embedded and stored.
        db_path (str): Path to save the FAISS vector database.

    Returns:
        FAISS: The FAISS vector database.
    """
    # Embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": device}, # use GPU or CPU
        encode_kwargs={"batch_size": batch_size, "normalize_embeddings": normal_embeddings} # fit with CPU
    )

    # Store documents in FAISS
    vector_db = FAISS.from_documents(
        doc_chunks, 
        embeddings,
        distance_strategy="COSINE" # change distance
    )
    vector_db.save_local(db_path)
    return vector_db

def save_bm25_retriever(doc_chunks, db_path):
    """
    Create and save BM25 retriever for future use with hybrid search.
    
    Args:
        doc_chunks (list): Document chunks for creating BM25Retriever
        db_path (str): Base path where to save the BM25 retriever
        
    Returns:
        str: Path to saved BM25 retriever
    """
    print("Creating BM25 retriever...")
    # Create BM25 retriever for keyword search
    bm25_retriever = BM25Retriever.from_documents(doc_chunks)
    bm25_retriever.k = 5
    
    # Save BM25 retriever for future use
    bm25_path = os.path.join(os.path.dirname(db_path), "bm25.pkl")
    try:
        with open(bm25_path, "wb") as f:
            pickle.dump(bm25_retriever, f)
        print(f"Saved BM25 retriever to {bm25_path}")
        return bm25_path
    except Exception as e:
        print(f"Failed to save BM25 retriever: {e}")
        return None

def retrieve_documents(query: str, db_path: str, top_k: int) -> list:
    """
    Retrieve the most relevant documents based on a query using vector search.

    Args:
        query (str): The search query.
        db_path (str): Path where the FAISS vector database is stored.
        top_k (int): Number of top results to retrieve.

    Returns:
        list: The top `k` most relevant documents.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )  
    vector_db = FAISS.load_local(db_path, embeddings)

    # Perform similarity search in the vector database
    results = vector_db.similarity_search(query, k=top_k)
    
    return results
def check_and_prepare_paths(db_path):
    """
    Check if vector DB and BM25 files exist and prepare to overwrite them.
    
    Args:
        db_path (str): Path to the vector database
        
    Returns:
        tuple: (index_path, bm25_path) paths to the files
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Define paths
    index_faiss_path = os.path.join(db_path, "index.faiss")
    index_pkl_path = os.path.join(db_path, "index.pkl")
    bm25_path = os.path.join(os.path.dirname(db_path), "bm25.pkl")
    
    # Check if files exist
    if os.path.exists(index_faiss_path):
        print(f"Found existing vector database file: {index_faiss_path} (will be overwritten)")
        try:
            os.remove(index_faiss_path)
            print(f"Deleted: {index_faiss_path}")
        except Exception as e:
            print(f"Warning: Could not delete {index_faiss_path}: {e}")
    
    if os.path.exists(index_pkl_path):
        print(f"Found existing vector database file: {index_pkl_path} (will be overwritten)")
        try:
            os.remove(index_pkl_path)
            print(f"Deleted: {index_pkl_path}")
        except Exception as e:
            print(f"Warning: Could not delete {index_pkl_path}: {e}")
    
    if os.path.exists(bm25_path):
        print(f"Found existing BM25 file: {bm25_path} (will be overwritten)")
        try:
            os.remove(bm25_path)
            print(f"Deleted: {bm25_path}")
        except Exception as e:
            print(f"Warning: Could not delete {bm25_path}: {e}")
    
    return (db_path, bm25_path)

def main():
    # Initialize configuration
    config = Config()
    db_path = os.path.abspath(config.get_config()["vector_db_path"])
    
    print("Checking for existing files...")
    db_path, bm25_path_expected = check_and_prepare_paths(db_path)
    print("Paths prepared for new files.")
    # Connect to database and fetch data
    # Read file from s3 
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=st.secrets["S3_BUCKET_JOB"], Key = "job_data.csv")
    content = response["Body"].read().decode("utf-8")

    # convert content into Data Frame
    df = pd.read_csv(StringIO(content))
    print(df)

    # Create documents and chunk them
    print("Creating document chunks...")
    documents = load_documents(df)
    print(documents)
    doc_chunks = chunk_text(documents)
    print(f"Created {len(doc_chunks)} document chunks")
    
    # Create and save vector database
    print("Creating vector database...")
    vector_db = embed_and_store(doc_chunks, db_path)
    print(f"Created embedding and store vector")

    # create bm25 file
    print("Createting bm25...")
    bm25_path = save_bm25_retriever(doc_chunks, db_path)
    print(f"Created bm25")


# Run main to build the database and hybrid search
if __name__ == "__main__":
    main()
    # Uncomment to run the example comparison
    # example_usage()