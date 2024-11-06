from src.utils import load_pdf, text_split, download_hugging_face_embeddings
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv

# Initializing the Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(host=os.getenv("PINECONE_HOST"))

extracted_data = load_pdf("data/")
text_chunks = text_split(extracted_data)
embeddings = download_hugging_face_embeddings()

# Create embeddings for each of the text chunk and upsert to the Pinecone
i = 1
for t in text_chunks:
    
    vectors.append(
        {
            "id":f"vec{i}",
            "values": embeddings.embed_query(t.page_content),
            "metadata": {"text": t.page_content}
        }
        
    )
    i += 1

    # Only length of a vector greater than 1000 will activate this part 
    if len(vectors) == 1000:
        upsert_response = index.upsert(
            vectors, namespace= os.getenv("namespace")
        )
        vectors = []

upsert_response = index.upsert(
    vectors, namespace= os.getenv("namespace")
)

