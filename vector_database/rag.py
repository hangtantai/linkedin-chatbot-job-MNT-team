# Utilization
import pandas as pd
# Document and Splitter
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Embeddings
# from langchain_community.embeddings import TensorflowHubEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from streamlit_app.db.db_connection import Database
# Vector Store
from langchain_community.vectorstores import FAISS
# QNA
from langchain.chains import RetrievalQA
from streamlit_app.utils.config import Config
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
def load_documents(data: pd.DataFrame) -> list:
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
        \nJob Location: {row["job_location"]}
        \nTime of the job that is posted in Linkedin: {row["job_time_posted"]}
        \nApplicants of Job that is applied: {row["job_applicants_applied"]}
        \nRole of the job: {row["job_role"]}
        \nDetails of the job: it include: qualification, requirement, beneficial and something like that: {row["job_details"]}''',
        metadata={"Job title": row["job_title"]},
    )
    for _, row in data.iterrows()
    ]
    return documents

def chunk_text(documents: list, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
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
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = splitter.split_documents(documents)
    return split_docs

def embed_and_store(doc_chunks: list, db_path: str):
    """
    Embed the document chunks and store them in a vector database (FAISS).

    Args:
        doc_chunks (list): The chunked documents to be embedded and stored.
        db_path (str): Path to save the FAISS vector database.

    Returns:
        FAISS: The FAISS vector database.
    """
    # Use TensorFlowHubEmbeddings for embedding documents
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Store the documents in FAISS (a vector database)
    vector_db = FAISS.from_documents(doc_chunks, embeddings)

    # Save the vector database to disk
    vector_db.save_local(db_path)
    return vector_db

def retrieve_documents(query: str, db_path: str, top_k: int) -> list:
    """
    Retrieve the most relevant documents based on a query.

    Args:
        query (str): The search query.
        db_path (str): Path where the FAISS vector database is stored.
        top_k (int): Number of top results to retrieve.

    Returns:
        list: The top `k` most relevant documents.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )  # Or use another embedding model
    vector_db = FAISS.load_local(db_path, embeddings)

    # Perform similarity search in the vector database
    results = vector_db.similarity_search(query, k=top_k)
    return results

def main():
    # Initialize configuration
    config = Config()
    # just run 3.10
    # pip install tensorflow-hub
    # pip install tensorflow_text

    # 3.11
    # pip install sentence-transformers
    db = Database()
    df_list = db.fetch_data()
    df = pd.DataFrame(df_list)

    documents = load_documents(df)
    doc_chunks = chunk_text(documents)
    vector_db = embed_and_store(doc_chunks, db_path=os.path.abspath(config.get_config()["vector_db_path"]))

main()

# LLM + RAG(tools)

# LLM knowledge (trained) function calling