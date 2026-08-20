import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "data/chroma_db"
DOCUMENTS_PATH = "data/documents"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name="company_documents",
    embedding_function=embedding_fn
)

def ingest_documents():
    files = [f for f in os.listdir(DOCUMENTS_PATH) if f.endswith(".txt")]

    for filename in files:
        company_name = filename.replace(".txt", "")
        filepath = os.path.join(DOCUMENTS_PATH, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        collection.add(
            documents=[content],      
            ids=[company_name],         
            metadatas=[{"company": company_name}]
        )

        print(f"✅ Ingested: {company_name}")

    print(f"\nDone. Total documents in collection: {collection.count()}")


if __name__ == "__main__":
    ingest_documents()

