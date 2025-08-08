import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# Pinecone environment settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")  # e.g., "aws-us-east-1"
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Extract cloud and region (e.g., "aws-us-east-1" → "aws", "us-east-1")
cloud, region = PINECONE_ENV.split("-", 1)

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if not exists
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud=cloud, region=region)
    )

# Connect to index
index = pc.Index(PINECONE_INDEX_NAME)

# Load sentence transformer
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_and_upload_assignments(assignments):
    """Embed assignments and upload to Pinecone"""
    vectors = embed_model.encode(assignments).tolist()
    pinecone_vectors = [
        {"id": f"assign-{i}", "values": vec, "metadata": {"text": text}}
        for i, (vec, text) in enumerate(zip(vectors, assignments))
    ]
    index.upsert(vectors=pinecone_vectors)
    return f"{len(assignments)} assignments uploaded to Pinecone."

def search_similar_assignments(query, top_k=3):
    """Search Pinecone index for similar assignments"""
    query_vec = embed_model.encode([query])[0].tolist()
    results = index.query(vector=query_vec, top_k=top_k, include_metadata=True)
    return [match['metadata']['text'] for match in results['matches']]
