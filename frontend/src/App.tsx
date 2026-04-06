import { useState } from "react";
import "./index.css";

interface Movie {
  rank: number;
  movie_name: string;
  genre: string[];
  story: string;
  mood: string[];
  cast: string[];
  industry: string;
  year_of_release: number;
  match_score: number;
  match_reason: string;
  omdb_data?: {
    Title: string;
    Year: string;
    Rated: string;
    Runtime: string;
    Genre: string;
    Director: string;
    Actors: string;
    Plot: string;
    Language: string;
    Country: string;
    Awards: string;
    Poster: string;
    imdbRating: string;
    imdbVotes: string;
    Type: string;
  } | null;
}

interface ApiResponse {
  original_story: string;
  recommended_movies: Movie[];
}

function App() {
  const [story, setStory] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [error, setError] = useState("");
  const [excludeList, setExcludeList] = useState<string[]>([]);

  const fetchRecommendations = async (isLoadMore: boolean) => {
    if (!story.trim()) {
      setError("Please share your story first.");
      return;
    }

    try {
      if (isLoadMore) {
        setLoadingMore(true);
      } else {
        setLoading(true);
        setExcludeList([]);
      }
      
      setError("");
      
      let currentExclude = isLoadMore ? excludeList : [];

      const response = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ story, exclude: currentExclude }),
      });

      if (!response.ok) {
        let msg = "Failed to fetch recommendations.";
        try {
          const body = await response.json();
          msg = body.detail || msg;
        } catch {}
        throw new Error(msg);
      }

      const data: any = await response.json();
      
      if (data.error) {
        throw new Error(`LLM Error: ${data.error}`);
      }
      if (!data.recommended_movies || !Array.isArray(data.recommended_movies)) {
        throw new Error("Invalid response format: 'recommended_movies' list missing from API output.");
      }
      
      if (isLoadMore && result) {
        setResult({
          ...data,
          recommended_movies: [
            ...result.recommended_movies,
            ...data.recommended_movies
          ]
        });
      } else {
        setResult(data);
      }
      
      if (data.recommended_movies) {
        const newNames = data.recommended_movies.map(m => m.movie_name);
        setExcludeList(isLoadMore ? [...currentExclude, ...newNames] : newNames);
      }

    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      if (isLoadMore) {
        setLoadingMore(false);
      } else {
        setLoading(false);
      }
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>CineMatch™</h1>
        <p>Advanced RAG + LLM Movie Recommendations based on your personal story</p>
      </header>

      <section className="input-section">
        <textarea
          placeholder="Tell me how you are feeling, what kind of world you want to dive into, or a story you'd like to experience..."
          value={story}
          onChange={(e) => setStory(e.target.value)}
        />
        {error && <div style={{ color: "#ef4444", marginTop: "1rem" }}>{error}</div>}
        <button
          className="generate-btn"
          onClick={() => {
            setResult(null);
            fetchRecommendations(false);
          }}
          disabled={loading || !story.trim()}
        >
          {loading ? (
            <>
              <div className="loader"></div>
              <span>Analyzing your vibe...</span>
            </>
          ) : (
            <span>✨ Find My Perfect Movies</span>
          )}
        </button>
      </section>

      {result && result.recommended_movies && result.recommended_movies.length > 0 && (
        <section className="results-container">
          <div className="results-title">
            <span>🎬</span> Tops Picks For You
          </div>

          {result.recommended_movies.map((movie, idx) => (
            <div
              className="movie-card"
              key={`${idx}-${movie.movie_name}`}
              style={{ animationDelay: `${(idx % 5) * 0.15}s` }}
            >
              <div className="movie-poster">
                {movie.omdb_data?.Poster && movie.omdb_data.Poster !== "N/A" ? (
                  <img src={movie.omdb_data.Poster} alt={`${movie.movie_name} Poster`} />
                ) : (
                  <div className="poster-placeholder">🎥</div>
                )}
              </div>

              <div className="movie-content">
                <div className="movie-header">
                  <div>
                    <h2 className="movie-title">
                      {movie.omdb_data?.Title || movie.movie_name}
                    </h2>
                    <div className="movie-meta">
                      <span>{movie.omdb_data?.Year || movie.year_of_release}</span>
                      <span>•</span>
                      <span>{movie.industry || movie.omdb_data?.Country}</span>
                      {movie.omdb_data?.Runtime && (
                        <>
                          <span>•</span>
                          <span>{movie.omdb_data.Runtime}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "0.5rem", flexDirection: "column", alignItems: "flex-end" }}>
                    {movie.omdb_data?.imdbRating && movie.omdb_data.imdbRating !== "N/A" && (
                      <div className="rating-badge">
                        ⭐ {movie.omdb_data.imdbRating}
                      </div>
                    )}
                    <div className="match-score">Match: {movie.match_score} pts</div>
                  </div>
                </div>

                <div className="movie-genres">
                  {(movie.omdb_data?.Genre ? movie.omdb_data.Genre.split(', ') : movie.genre).map((g, i) => (
                    <span className="genre-tag" key={i}>
                      {g}
                    </span>
                  ))}
                  {movie.mood && movie.mood.slice(0,3).map((m, i) => (
                    <span className="genre-tag" key={`mood-${i}`} style={{ background: 'rgba(236, 72, 153, 0.1)', color: '#f472b6', borderColor: 'rgba(236, 72, 153, 0.3)' }}>
                      {m}
                    </span>
                  ))}
                </div>

                <div className="movie-reason">
                  <h4>💡 Why we recommend this</h4>
                  <p>{movie.match_reason}</p>
                </div>

                {movie.omdb_data?.Plot && movie.omdb_data.Plot !== "N/A" ? (
                  <p className="movie-omdb-plot">{movie.omdb_data.Plot}</p>
                ) : (
                  <p className="movie-omdb-plot">{movie.story}</p>
                )}
              </div>
            </div>
          ))}
          
          <button
            className="generate-btn"
            style={{ 
              marginTop: "2rem", 
              background: "linear-gradient(135deg, #3b82f6, #ec4899)",
              maxWidth: "400px",
              alignSelf: "center"
            }}
            onClick={() => fetchRecommendations(true)}
            disabled={loadingMore || loading}
          >
            {loadingMore ? (
              <>
                <div className="loader"></div>
                <span>Discovering more...</span>
              </>
            ) : (
              <span>🔮 Bring Me More Ideas</span>
            )}
          </button>
        </section>
      )}
    </div>
  );
}

export default App;
