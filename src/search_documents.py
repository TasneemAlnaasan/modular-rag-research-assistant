import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "data/chroma_db"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name="company_documents",
    embedding_function=embedding_fn
)


def search_documents(question: str, n_results: int = 2) -> str:
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )

    documents = results["documents"][0]  
    if not documents:
        return None

    return "\n\n".join(documents)


if __name__ == "__main__":
    test_question = "What is Anthropic's vision?"
    result = search_documents(test_question)
    print(result)
