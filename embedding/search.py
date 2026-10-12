import faiss
import numpy as np
import json

from embedding import generate_embedding


# ----------------------------------------
# File paths
# ----------------------------------------

INDEX_PATH = "./vector_store/storage.index"
METADATA_PATH = "./vector_store/metadata.json"


# ----------------------------------------
# Load FAISS index
# ----------------------------------------

index = faiss.read_index(INDEX_PATH)

print("Vectors loaded:", index.ntotal)


# ----------------------------------------
# Load metadata
# ----------------------------------------

with open(METADATA_PATH, "r") as file:
    metadata = json.load(file)


# ----------------------------------------
# Query
# ----------------------------------------

query = "What is the required time limit for reporting a security incident?"


# ----------------------------------------
# Generate query embedding
# ----------------------------------------

query_embedding = generate_embedding(query)

query_embedding = np.asarray(
    query_embedding
).astype("float32")
query_embedding = query_embedding.reshape(1, -1)


# ----------------------------------------
# Number of results
# ----------------------------------------

k = 10


# ----------------------------------------
# Search FAISS
# ----------------------------------------

distances, indices = index.search(
    query_embedding,
    k
)


# ----------------------------------------
# Display results
# ----------------------------------------

print("\nQuery:")
print(query)

print("\nSearch Results:")

for distance, idx in zip(distances[0], indices[0]):

    text = metadata[str(idx)]

    print("\nVector ID:", idx)
    print("L2 Distance:", round(float(distance), 4))
    print("Text:", text)