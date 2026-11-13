import os
import sys
import numpy as np

# Import the teammate's embedding function directly, without duplicating it
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "embedding"))
from embedding import generate_embedding

SIMILARITY_THRESHOLD = 0.80  # tune this: higher = stricter grouping


def _cosine_similarity(a, b):
    """Vectors from generate_embedding() are already normalized, so dot product = cosine similarity."""
    return float(np.dot(a, b))


def embed_claims(claims):
    """Generate one embedding per claim, based on its original sentence text."""
    texts = [c["original_text"] for c in claims]
    embeddings = [generate_embedding(t) for t in texts]
    return np.asarray(embeddings).astype("float32")


def cluster_claims(claims, threshold=SIMILARITY_THRESHOLD):
    """
    Groups claims into topic clusters using embedding similarity.
    Greedy approach: each claim joins the most similar existing cluster
    if similarity >= threshold, otherwise starts a new cluster.
    Returns a list of clusters, each a list of claim dicts.
    """
    if not claims:
        return []

    embeddings = embed_claims(claims)
    clusters = []  # each: {"centroid": vector, "claims": [...], "embeddings": [...]}

    for claim, embedding in zip(claims, embeddings):
        best_cluster = None
        best_score = -1

        for cluster in clusters:
            score = _cosine_similarity(cluster["centroid"], embedding)
            if score > best_score:
                best_score = score
                best_cluster = cluster

        if best_cluster is not None and best_score >= threshold:
            best_cluster["claims"].append(claim)
            best_cluster["embeddings"].append(embedding)
            avg = np.mean(best_cluster["embeddings"], axis=0)
            norm = np.linalg.norm(avg)
            best_cluster["centroid"] = avg / norm if norm > 0 else avg
        else:
            clusters.append({
                "centroid": embedding,
                "claims": [claim],
                "embeddings": [embedding]
            })

    return [{"claims": c["claims"]} for c in clusters]