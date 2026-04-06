import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from query import GenerateRecommendation, llm
from rag import get_similar_movies

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

app = FastAPI(
    title="Movie Recommendation API",
    description="Recommends movies based on user's story using RAG and Groq LLM",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_omdb_details(title: str, year: int = None):
    if not OMDB_API_KEY:
        return None
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
    if year:
        url += f"&y={year}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return data
    except Exception:
        pass
    return None

class StoryRequest(BaseModel):
    story: str
    exclude: list[str] = []

@app.post("/recommend")
def recommend_movies(request: StoryRequest):
    if not request.story:
        raise HTTPException(status_code=400, detail="Story cannot be empty")
        
    try:
        # Step 1: Retrieve similar movies candidates using FAISS from MongoDB entries
        movies_context = get_similar_movies(request.story, k=25, exclude_names=request.exclude)
        
        # Step 2: Let LLM score and filter based on strict constraints
        recommendation_result = GenerateRecommendation(request.story, movies_context, llm)
        
        # Step 3: Fetch OMDB details for each recommended movie
        if isinstance(recommendation_result, dict) and "recommended_movies" in recommendation_result:
            for movie in recommendation_result["recommended_movies"]:
                omdb_data = fetch_omdb_details(movie.get("movie_name"), movie.get("year_of_release"))
                if omdb_data:
                    movie["omdb_data"] = omdb_data
                    
        return recommendation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

