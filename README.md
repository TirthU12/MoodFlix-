# 🎬 CineMatch RAG Movie Recommender

![CineMatch Hero](https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=2670&auto=format&fit=crop)

CineMatch is a modern, AI-powered movie recommendation system. Instead of simply filtering by basic genres, users provide a personal story, mood, or setting they want to experience. 

The application utilizes **RAG (Retrieval-Augmented Generation)** through **FAISS Contextual Vector Search** and **LangChain** to pull highly accurate localized candidate movies before handing them off to the **Groq LLM** (e.g. `llama-3.3-70b-versatile`) for rigorous, intelligent matching and scoring. Final results are dynamically augmented with real-world metadata including Posters and Ratings via the **OMDB API**.

## 🚀 Features

- **Semantic Story Matching:** Describe your mood or story and the FAISS vector database retrieves semantically related movie candidates.
- **LLM Refinement:** Candidates are scored and strictly pruned by an advanced Groq LLM based on hidden criteria and constraints.
- **OMDB API Enrichment:** Fetches live movie posters, runtimes, and IMDb ratings on the fly to complement the UI.
- **Infinite Discovery:** An intelligent "Bring Me More Ideas" system that feeds omitted history to the API ensuring zero duplicate results.
- **Premium Glassmorphism UI:** Built with React and Vite, featuring smooth animations, dynamic loading states, and dark mode aesthetics.

## 🛠 Tech Stack

**Backend (Python):**
- [FastAPI](https://fastapi.tiangolo.com/) (Web Framework)
- [LangChain](https://www.langchain.com/) (Workflow Orchestration)
- [FAISS](https://faiss.ai/) (Similarity Vector Search)
- [HuggingFace](https://huggingface.co/) `sentence-transformers/all-mpnet-base-v2`
- [Groq AI](https://groq.com/) (Extremely fast LLM interference)
- [uv](https://astral.sh/uv) (Extremely fast Python package manager)

**Frontend (React):**
- [Vite JS](https://vitejs.dev/)
- React TypeScript 
- Custom Vanilla CSS Design System 
- [Bun](https://bun.sh/) (Fast JavaScript runtime and package manager)

---

## 💻 Running the Application Locally

### Prerequisites
Make sure you have [uv](https://github.com/astral-sh/uv) installed for the backend packages, and [bun](https://bun.sh) installed for the frontend components.


### 1. Configure Environment Variables
Inside the `Rag project` directory, ensure a `.env` file exists with your actual API keys:

```ini
GROQ_API_KEY=gsk_your_groq_key...
OMDB_API_KEY=your_omdb_key
```

### 2. Start the Backend API
Navigate to your backend directory and run the FastAPI server:
```bash
cd "Rag project"
uv add requests json-repair
uv run uvicorn main:app --reload
```
The API will perform its first-time FAISS vector database generation and should begin running at `http://127.0.0.1:8000`. 


### 3. Start the Frontend Application
In a separate terminal, traverse to the React frontend folder:
```bash
cd frontend
bun install
bun run dev
```

The frontend application will boot up at `http://localhost:5173`. Open it in your web browser and start matching!

---

## 🤝 Contributing
Contributions, issues and feature requests are welcome! 
Feel free to check out the issues page.
