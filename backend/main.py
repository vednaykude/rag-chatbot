# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import requests
from typing import List
import re
import os
from sentence_transformers import SentenceTransformer
import ollama

app = FastAPI(title="RAG Chatbot API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Initialize sentence transformer for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Create or get collection
collection_name = "wikipedia_articles"
try:
    collection = chroma_client.get_collection(collection_name)
    print(f"Loaded existing collection: {collection_name}")
except:
    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"description": "Wikipedia articles for RAG chatbot"}
    )
    print(f"Created new collection: {collection_name}")

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

def fetch_wikipedia_articles():
    """Fetch sample Wikipedia articles as our data source"""
    topics = [
        "Artificial Intelligence",
        "Machine Learning", 
        "Natural Language Processing",
        "Deep Learning",
        "Computer Vision",
        "Python Programming",
        "Data Science",
        "Neural Networks",
        "Transformer Models",
        "Large Language Models"
    ]
    
    articles = []
    
    for topic in topics:
        try:
            # Get Wikipedia page summary
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'extract' in data and data['extract']:
                    articles.append({
                        'title': data['title'],
                        'content': data['extract'],
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    })
                    print(f"Fetched: {data['title']}")
            
        except Exception as e:
            print(f"Error fetching {topic}: {e}")
            continue
    
    return articles

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

def populate_database():
    """Populate ChromaDB with Wikipedia articles"""
    # Check if collection already has data
    if collection.count() > 0:
        print(f"Collection already has {collection.count()} documents")
        return
    
    print("Fetching Wikipedia articles...")
    articles = fetch_wikipedia_articles()
    
    if not articles:
        print("No articles fetched. Please check your internet connection.")
        return
    
    documents = []
    metadatas = []
    ids = []
    
    doc_id = 0
    
    for article in articles:
        # Chunk the article content
        chunks = chunk_text(article['content'])
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                'title': article['title'],
                'url': article['url'],
                'chunk_id': i
            })
            ids.append(f"{doc_id}_{i}")
        
        doc_id += 1
    
    # Generate embeddings and add to ChromaDB
    print(f"Adding {len(documents)} document chunks to ChromaDB...")
    embeddings = embedding_model.encode(documents).tolist()
    
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully added {len(documents)} documents to the database")

def query_documents(query: str, top_k: int = 3) -> List[dict]:
    """Query similar documents from ChromaDB"""
    query_embedding = embedding_model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    documents = []
    for i in range(len(results['documents'][0])):
        documents.append({
            'content': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
            'distance': results['distances'][0][i]
        })
    
    return documents

def generate_answer(question: str, context_docs: List[dict]) -> str:
    """Generate answer using Llama3 via Ollama"""
    # Prepare context from retrieved documents
    context = "\n\n".join([doc['content'] for doc in context_docs])
    
    prompt = f"""Based on the following context, please answer the question. If the answer cannot be found in the context, please say so.

Context:
{context}

Question: {question}

Answer:"""
    
    try:
        # Call Ollama API for Llama3
        response = ollama.generate(
            model='llama3',
            prompt=prompt,
            stream=False
        )
        return response['response']
    
    except Exception as e:
        return f"Error generating response: {str(e)}. Please make sure Ollama is running and Llama3 model is installed."

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup"""
    populate_database()

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}

@app.get("/health")
async def health_check():
    doc_count = collection.count()
    return {
        "status": "healthy",
        "database_documents": doc_count,
        "ollama_available": check_ollama_connection()
    }

def check_ollama_connection():
    """Check if Ollama is available"""
    try:
        response = ollama.list()
        return True
    except:
        return False

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """Main chat endpoint"""
    try:
        # Retrieve relevant documents
        relevant_docs = query_documents(request.question, request.top_k)
        
        if not relevant_docs:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # Generate answer using Llama3
        answer = generate_answer(request.question, relevant_docs)
        
        # Extract sources
        sources = []
        for doc in relevant_docs:
            source = f"{doc['metadata']['title']}"
            if doc['metadata'].get('url'):
                source += f" ({doc['metadata']['url']})"
            sources.append(source)
        
        return QueryResponse(answer=answer, sources=list(set(sources)))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/count")
async def get_document_count():
    """Get the number of documents in the database"""
    return {"count": collection.count()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)