from sentence_transformers import SentenceTransformer
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME,local_files_only=True)

def generate_embedding(text):
    return model.encode(text,
                        convert_to_numpy=True,
                        normalize_embeddings=True)

