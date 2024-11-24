import os
from groq import Groq

# Initialize the Groq client
client = Groq(
    api_key="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",  # Ensure GROQ_API_KEY is set in your environment
)

from sentence_transformers import SentenceTransformer
import faiss

# Load a model to generate embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Your documents
with open("test.txt", "r") as file:
    documents = [line.strip() for line in file.readlines() if line.strip()]

# Generate embeddings and store them in FAISS
doc_embeddings = embedding_model.encode(documents)
index = faiss.IndexFlatL2(doc_embeddings.shape[1])  # L2 distance
index.add(doc_embeddings)

def retrieve_documents(query, k=3):
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, k)
    return [documents[i] for i in indices[0]]

def rag_pipeline(query):
    # Step 1: Retrieve relevant documents
    relevant_docs = retrieve_documents(query)
    
    # Step 2: Combine the query with retrieved context
    augmented_query = query + "\n\n" + "Relevant Context:\n" + "\n".join(relevant_docs)
    
    # Step 3: Generate a response using Groq's API
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": augmented_query},
        ],
        model="llama3-8b-8192",  # Replace with your preferred model
    )
    
    # Step 4: Return the generated response
    return chat_completion.choices[0].message.content

query = "What is the website about?"
response = rag_pipeline(query)
print("Generated Response:", response)
