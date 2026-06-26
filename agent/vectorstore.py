import os
import json
import math
import requests
from config import JINA_API_KEY, EMBEDDING_MODEL, EMBEDDING_URL, SEMANTIC_FILE


def get_embedding(text: str) -> list[float]:
    """Converts text into a vector using Jina Embeddings API."""
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    data = {
        "model": EMBEDDING_MODEL,
        "input": [text]
    }
    
    response = requests.post(EMBEDDING_URL, headers=headers, json=data)
    response.raise_for_status()
    
    # Extract the embedding array from Jina's response payload
    return response.json()["data"][0]["embedding"]

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculates semantic similarity between two vectors (0.0 to 1.0)."""
    dot_product = sum(a * b for a, b in zip[tuple[float, float]](vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if not magnitude1 or not magnitude2:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def save_semantic_memory(text: str):
    """Embeds and saves a new lesson/heuristic to the JSON vector store."""
    vector = get_embedding(text)
    memory_item = {"text": text, "vector": vector}
    
    if os.path.exists(SEMANTIC_FILE):
        with open(SEMANTIC_FILE, "r") as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = []
    else:
        db = []
        
    # Prevent exact duplicates
    if not any(item["text"] == text for item in db):
        db.append(memory_item)
        with open(SEMANTIC_FILE, "w") as f:
            json.dump(db, f, indent=2)

def search_semantic_memory(query: str, top_k: int = 3) -> list[str]:
    """Embeds a query and returns the most relevant saved heuristics."""
    if not os.path.exists(SEMANTIC_FILE):
        return []
        
    with open(SEMANTIC_FILE, "r") as f:
        try:
            db = json.load(f)
        except json.JSONDecodeError:
            return []
            
    if not db:
        return []

    query_vector = get_embedding(query)
    
    # Score all memories
    scored_memories = []
    for item in db:
        score = cosine_similarity(query_vector, item["vector"])
        scored_memories.append((score, item["text"]))
        
    # Sort by highest score first
    scored_memories.sort(key=lambda x: x[0], reverse=True)
    
    # Return the text of the top_k results
    return [text for score, text in scored_memories[:top_k]]