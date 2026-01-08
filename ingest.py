import os
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# --- CONFIG ---
TARGET_FOLDER = "./target_code"
DB_PATH = "./qdrant_db"
COLLECTION_NAME = "codebase_index"

def ingest():
    print("⚙️  Starting Ingestion...")

    # 1. Load Code
    if not os.path.exists(TARGET_FOLDER):
        os.makedirs(TARGET_FOLDER)
        print(f"⚠️  Created {TARGET_FOLDER}. Please add files!")
        return

    loader = GenericLoader.from_filesystem(
        TARGET_FOLDER,
        glob="**/*",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
    )
    documents = loader.load()
    if not documents:
        print("⚠️  No files found. Skipping.")
        return
        
    print(f"📄 Loaded {len(documents)} files.")

    # 2. Split Code
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=500, 
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"🧩 Split into {len(chunks)} code chunks.")

    # 3. Connect to Database (Initialize Client)
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    client = QdrantClient(path=DB_PATH)
    
    # 4. Reset Collection (Clean slate)
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
        
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # 5. THE FIX: Instantiate Store first, then add documents
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    print("💾 Uploading vectors...")
    vector_store.add_documents(chunks)
    
    print("✅ Ingestion Complete! Database saved to ./qdrant_db")
    client.close()

if __name__ == "__main__":
    ingest()