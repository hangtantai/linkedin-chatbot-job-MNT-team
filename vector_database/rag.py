# Utilization
import os
import pickle
import pandas as pd
import streamlit as st
from io import StringIO 
import sys
import boto3
import shutil
# Document and Splitter
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
# Vector Store
from langchain_community.vectorstores import FAISS 
# Hybrid Search components
from langchain_community.retrievers import BM25Retriever
# Check if running on Streamlit Cloud
if "mnt" in os.getcwd():
    os.chdir("/mount/src/linkedin-chatbot-job-mnt-team/")
    sys.path.append("/mount/src/linkedin-chatbot-job-mnt-team/")
# QNA
from streamlit_app.utils.config import Config

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Variables
config = Config().get_config()
chunk_size = config["chunk_size"]
chunk_overlap = config["chunk_overlap"]
bucket_vectordb = config["bucket_vectordb"]
prefix = config["prefix_vectodb"]
batch_size = config["batch_size"]
device = config["device"]
distance = config["distance"]
normal_embeddings = config["normal_embeddings"]
s3_key_bm25 = config["s3_key"]
bm25_file = config["bm25_file"]
bucket_job = config["bucket_job"]

def load_documents(df: pd.DataFrame) -> list:
    """
    Convert data into Documents

    Args:
        Data frame: Data to be converted into documents

    Returns:
        Documents includes page content and metadata
    """
    # Convert into documents
    # Convert into documents
    documents = [
        Document(
            page_content=f'''Job Title: {row["job_title"]}
            \nCompany Name: {row["company_name"]}
            \nJob Location: {row["job_location"]}
            \nUrl to detail job in Linkedin: {row["url"]}
            \nTime of the job that is posted in Linkedin: {row["job_time_posted"]}
            \nApplicants of Job that is applied: {row["job_applicants_applied"]}
            \nRole of the job: {row["job_role"]}
            \nDetails of the job: it include: qualification, requirement, beneficial and something like that: {row["job_details"]}''',
            metadata={
                "job_title": row["job_title"],
                "company_name": row["company_name"],
                "job_location": row["job_location"],
                "job_url": row["url"]
            },
        )
        for _, row in df.iterrows()
    ]
    return documents

def chunk_text(documents: list, chunk_size: int = chunk_size, chunk_overlap: int = chunk_overlap) -> list:
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

# Add this function to upload a directory to S3
def upload_directory_to_s3(local_directory, bucket, s3_prefix):
    """
    Upload a directory to S3 bucket
    
    Args:
        local_directory (str): Local directory path
        bucket (str): S3 bucket name
        s3_prefix (str): S3 key prefix (folder path)
    """
    s3_client = boto3.client('s3')
    
    for root, dirs, files in os.walk(local_directory):
        for file in files:
            local_path = os.path.join(root, file)
            # Calculate relative path
            relative_path = os.path.relpath(local_path, local_directory)
            s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")
            
            print(f"Uploading {local_path} to s3://{bucket}/{s3_key}")
            s3_client.upload_file(local_path, bucket, s3_key)


def embed_and_store(model_name: str, doc_chunks: list, db_path: str, device: str = device, batch_size: int = batch_size, normal_embeddings: bool = normal_embeddings, distance: str = distance):
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
        model_name=model_name,
        model_kwargs={"device": device}, # use GPU or CPU
        encode_kwargs={"batch_size": batch_size, "normalize_embeddings": normal_embeddings} # fit with CPU
    )

    # Store documents in FAISS
    vector_db = FAISS.from_documents(
        doc_chunks, 
        embeddings,
        distance_strategy=distance # change distance
    )
    vector_db.save_local(db_path)
     # Upload to S3
    bucket_name = bucket_vectordb  # Use the same bucket name here
    upload_directory_to_s3(db_path, bucket_vectordb, prefix)
    print(f"Uploaded FAISS database to S3 bucket: {bucket_vectordb}/{prefix}")
    
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
    bm25_path = os.path.join(os.path.dirname(db_path), bm25_file)
    try:
        with open(bm25_path, "wb") as f:
            pickle.dump(bm25_retriever, f)
        print(f"Saved BM25 retriever to {bm25_path}")
         
        # Upload to S3
        bucket_name = bucket_vectordb  # Change to your preferred bucket name
        s3_client = boto3.client("s3")
        s3_client.upload_file(bm25_path, bucket_name, s3_key_bm25)  # Fix: use bm25_path instead of db_path
        
        print(f"Saved BM25 retriever to S3: s3://{bucket_vectordb}/{s3_key_bm25}")
        return bm25_path
    except Exception as e:
        print(f"Failed to save BM25 retriever: {e}")
        return None

# Update the check_and_prepare_paths function
def check_and_prepare_paths(db_path: str):
    """
    Check if vector DB and BM25 files exist and prepare to overwrite them.
    
    Args:
        db_path (str): Path to the vector database
        
    Returns:
        tuple: (db_path, bm25_path) paths to the files
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Define paths
    bm25_path = os.path.join(os.path.dirname(db_path), bm25_file)
    
    # Check if directory exists
    if os.path.exists(db_path) and os.path.isdir(db_path):
        print(f"Found existing FAISS directory: {db_path} (will be overwritten)")
        try:
            # Remove the entire directory
            shutil.rmtree(db_path)
            print(f"Deleted directory: {db_path}")
        except Exception as e:
            print(f"Warning: Could not delete {db_path}: {e}")
    
    # Create the directory
    os.makedirs(db_path, exist_ok=True)
    
    # Check if BM25 file exists
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
    config = Config().get_config()
    db_path = os.path.abspath(config["vector_db_path"])

    # Connect to database and fetch data
    # Read file from s3 
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket_job, Key = "processed_data.csv")
    content = response["Body"].read().decode("utf-8")

    # convert content into Data Frame
    df = pd.read_csv(StringIO(content))

    # Create documents and chunk them
    print("Creating document chunks...")
    documents = load_documents(df)
    doc_chunks = chunk_text(documents)
    print(f"Created {len(doc_chunks)} document chunks")
    
    # Create and save vector database using FAISS
    print("Creating FAISS vector database...")
    vector_db = embed_and_store(
        model_name=config["model_name_vectordb"],
        doc_chunks=doc_chunks, 
        db_path=db_path
    )
    print("Created embeddings and stored in FAISS database")

    # Create BM25 file
    print("Creating BM25 retriever...")
    bm25_path = save_bm25_retriever(doc_chunks, db_path)
    print(f"Created BM25 retriever at {bm25_path}")
    print("\nRAG system setup complete with FAISS!")

# Run main to build the database and hybrid search
if __name__ == "__main__":
    main()