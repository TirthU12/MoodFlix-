import os
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from db import movies

def initialize_vectorstore():
    docs = []
    
    for movie in movies:
        text = f"""
        Movie: {movie.get('movie_name', '')}
        Genre: {', '.join(movie.get('genre', []))}
        Story: {movie.get('story', '')}
        Mood: {', '.join(movie.get('mood', []))}
        Cast: {', '.join(movie.get('cast', []))}
        Industry: {movie.get('industry','')}
        Year: {movie.get('year_of_release', '')}
        """

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "movie_name": movie.get("movie_name", ""),
                    "genre": movie.get("genre", []),
                    "story": movie.get("story", ""),
                    "cast": movie.get("cast", []),
                    "year": movie.get("year_of_release", ""),
                    "mood": movie.get("mood", []),
                    "industry": movie.get("industry", "")
                }
            )
        )

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore

# Build global vectorstore when module is imported
print("Initializing FAISS vectorstore with movies from DB...")
vectorstore = initialize_vectorstore()
print("Vectorstore initialized.")

def get_similar_movies(query: str, k: int = 5, exclude_names: list = None):
    if exclude_names is None:
        exclude_names = []
        
    fetch_k = k + (len(exclude_names) * 3)
    docs = vectorstore.similarity_search(query, k=fetch_k)
    
    candidates = []
    for doc in docs:
        if doc.metadata.get("movie_name") not in exclude_names:
            candidates.append(doc.metadata)
        if len(candidates) == k:
            break
            
    return candidates