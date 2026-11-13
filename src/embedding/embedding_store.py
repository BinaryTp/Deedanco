import faiss
import numpy as np
import json
import os
import sys

from embedding import generate_embedding


# ----------------------------------------
# File paths
# ----------------------------------------

INDEX_PATH = "./vector_store/storage.index"
METADATA_PATH = "./vector_store/metadata.json"


# ----------------------------------------
# ADD FUNCTION
# ----------------------------------------

def add_embeddings(texts):

    # ----------------------------------------
    # Load existing metadata
    # ----------------------------------------

    if os.path.exists(METADATA_PATH):

        with open(METADATA_PATH, "r") as file:
            metadata = json.load(file)

    else:

        metadata = {}


    # ----------------------------------------
    # Find duplicate texts
    # ----------------------------------------

    existing_texts = set(metadata.values())

    new_texts = []

    for text in texts:

        if text in existing_texts:

            print("Duplicate skipped:", text)

        else:

            new_texts.append(text)


    # ----------------------------------------
    # Stop if everything is duplicate
    # ----------------------------------------

    if not new_texts:

        print("No new texts to add.")
        return


    # ----------------------------------------
    # Generate embeddings
    # ----------------------------------------

    embeddings = [
        generate_embedding(text)
        for text in new_texts
    ]

    embeddings = np.asarray(embeddings).astype("float32")

    print("Embedding shape:", embeddings.shape)


    # ----------------------------------------
    # Get vector dimension
    # ----------------------------------------

    dimension = embeddings.shape[1]


    # ----------------------------------------
    # Load or create FAISS index
    # ----------------------------------------

    if os.path.exists(INDEX_PATH):

        print("Existing FAISS index found.")

        index = faiss.read_index(INDEX_PATH)

    else:

        print("No existing FAISS index found.")
        print("Creating new FAISS index.")

        index = faiss.IndexFlatL2(dimension)


    # ----------------------------------------
    # Current number of vectors
    # ----------------------------------------

    start_id = index.ntotal


    # ----------------------------------------
    # Add new vectors
    # ----------------------------------------

    index.add(embeddings)


    print("Previously stored vectors:", start_id)
    print("New vectors added:", len(new_texts))
    print("Total vectors:", index.ntotal)


    # ----------------------------------------
    # Add metadata
    # ----------------------------------------

    for i, text in enumerate(new_texts):

        vector_id = start_id + i

        metadata[str(vector_id)] = text


    # ----------------------------------------
    # Save FAISS index
    # ----------------------------------------

    faiss.write_index(
        index,
        INDEX_PATH
    )


    # ----------------------------------------
    # Save metadata
    # ----------------------------------------

    with open(METADATA_PATH, "w") as file:

        json.dump(
            metadata,
            file,
            indent=4
        )


    print("FAISS index updated.")
    print("Metadata updated.")


# ----------------------------------------
# DELETE ALL FUNCTION
# ----------------------------------------

def delete_all():

    print("\nWARNING!")
    print("This will delete ALL stored embeddings and metadata.")

    confirmation = input(
        'Type "DELETE" to confirm: '
    )

    if confirmation != "DELETE":

        print("Deletion cancelled.")
        return

    # Delete FAISS index
    if os.path.exists(INDEX_PATH):

        os.remove(INDEX_PATH)
        print("FAISS index deleted.")

    else:

        print("FAISS index does not exist.")

    # Delete metadata
    if os.path.exists(METADATA_PATH):

        os.remove(METADATA_PATH)
        print("Metadata deleted.")

    else:

        print("Metadata file does not exist.")

    print("\nAll stored embedding data has been deleted.")


# ----------------------------------------
# MAIN PROGRAM
# ----------------------------------------

if len(sys.argv) < 2:

    print("Usage:")
    print("  python embedding_store.py add")
    print("  python embedding_store.py delete")

    sys.exit()


command = sys.argv[1]


# ----------------------------------------
# ADD
# ----------------------------------------

if command == "add":

    texts = [
        "Employees must submit their monthly attendance report by the 5th day of every month.",

        "Employees are required to submit their monthly attendance report by the 10th day of every month.",

        "All employees must complete the annual cybersecurity training before December 31.",

        "Employees must change their corporate password every 90 days.",

        "Employees may work remotely for up to three days per week with prior approval.",

        "Employees are not permitted to access confidential company information from personal devices.",

        "Employees must wear their official identification badge while inside the organization.",

        "All visitors must register at the reception desk before entering the office premises.",

        "Employees are entitled to 20 days of paid annual leave each calendar year.",

        "Security incidents must be reported to the IT security team within 30 minutes of discovery.",

        "Employees must submit their monthly attendance report by the 5th day of every month.",

        "Employees are required to submit their monthly attendance report by the 10th day of every month.",

        "Employees must wear their official identification badge while inside the organization.",

        "Employees may work remotely for a maximum of three days per week .",

        "Employees are prohibited from accessing confidential company information from personal devices."
    ]

    add_embeddings(texts)


# ----------------------------------------
# DELETE
# ----------------------------------------

elif command == "delete":

    delete_all()


# ----------------------------------------
# INVALID COMMAND
# ----------------------------------------

else:

    print("Invalid command.")

    print("\nUsage:")
    print("  python embedding_store.py add")
    print("  python embedding_store.py delete")