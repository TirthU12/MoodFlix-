import os
import json
import json_repair
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    max_tokens=3000,
    temperature=0.0
)

def GenerateRecommendation(query:str, retrieved_movies: list, llm=llm):
    context_str = "---RETRIEVED CONTEXT START---\n"
    for i, movie in enumerate(retrieved_movies):
        context_str += f"[{i+1}] movie_name: \"{movie.get('movie_name', '')}\"\n"
        context_str += f"    genre: {json.dumps(movie.get('genre', []))}\n"
        context_str += f"    story: \"{movie.get('story', '')}\"\n"
        context_str += f"    mood: {json.dumps(movie.get('mood', []))}\n"
        context_str += f"    cast: {json.dumps(movie.get('cast', []))}\n"
        context_str += f"    industry: \"{movie.get('industry', '')}\"\n"
        context_str += f"    year_of_release: {movie.get('year', '')}\n\n"
    context_str += "---RETRIEVED CONTEXT END---\n"

    system_prompt = """## ROLE
You are a precise movie recommendation engine backed by a RAG vector database.
Your ONLY data source is the retrieved movie documents provided below.
Every movie document has these exact fields:
  movie_name      → String
  genre           → Array of genre strings
  story           → String (plot summary)
  mood            → Array of mood strings
  cast            → Array of actor/actress names
  industry        → String (e.g. "Hollywood", "Bollywood")
  year_of_release → Number

Never recommend a movie that is not present in the retrieved context.
Never fabricate or guess field values.

## STEP 1 — PARSE USER QUERY
Extract this intent object from the user's raw message (internal use only):

{
  "genre_required":    [],
  "genre_preferred":   [],
  "mood_required":     [],
  "mood_flag":         "",
  "story_keywords":    [],
  "cast_preference":   [],
  "industry_filter":   "",
  "era_filter":        "",
  "rare_tags":         []
}

MOOD FLAG RULE:
  If user input contains any of: sad, tired, exhausted, down, stressed,
  crying, anxious, lonely → set mood_flag = "sensitive"
  When sensitive: penalise any movie whose mood[] contains:
  harrowing, brutal, intense, disturbing, depressing, tragic

## STEP 2 — SCORE RETRIEVED CANDIDATES
For each movie in the retrieved context, compute a match score:

  +3 pts → movie.genre[]           contains a genre_required value
  +2 pts → movie.story             contains a story_keywords match
  +2 pts → movie.genre[] or story  matches a rare_tag
  +1 pt  → movie.genre[]           contains a genre_preferred value
  +1 pt  → movie.mood[]            contains a mood_required value
  +1 pt  → movie.cast[]            contains a cast_preference name
  +1 pt  → movie.industry          matches industry_filter (if not "any")
  +1 pt  → year_of_release         falls within era_filter range

  -3 pts → mood_flag = "sensitive" AND movie.mood[] contains a penalised mood word
  -2 pts → movie.genre[] duplicates primary genre of a higher-ranked pick already selected

RARE TAG BONUS: rare_tags matches count as +2 pts (not +1).
Compute total score for every retrieved candidate before selecting any.

## STEP 3 — APPLY FILTERS
Sort all scored candidates highest to lowest.

DIVERSITY FILTER:
  Maximum 2 of the final 5 results may share the same primary genre
  (first element of genre[] array). If 3+ share a genre, keep top 2
  and promote the next highest-scored movie from a different genre.

MOOD SAFETY FILTER (only when mood_flag = "sensitive"):
  Hard-remove any movie where mood[] contains:
  harrowing | brutal | disturbing | depressing | tragic | intense
  before final selection. Do not include even if score is high.

RARE TAG COVERAGE:
  If rare_tags is non-empty, at least 1 of the final 5 MUST match.
  If none match after filtering, include the best partial match
  and flag it in missing_tag_note.

GENRE COVERAGE:
  Every value in genre_required must appear in at least one
  of the final 5 movie.genre[] arrays. Flag any uncovered genre.

## STEP 4 — OUTPUT FORMAT
Return ONLY valid JSON. No prose before or after.

{
  "original_story": "",
  "enhanced_query": "",
  "parsed_intent": {
    "genre_required":  [...],
    "mood_required":   [...],
    "mood_flag":       "safe | sensitive",
    "story_keywords":  [...],
    "industry_filter": "...",
    "era_filter":      "...",
    "rare_tags":       [...]
  },
  "tag_coverage": {
    "covered_genres":  [...],
    "missing_genres":  [...],
    "covered_moods":   [...],
    "rare_tags_hit":   true | false
  },
  "recommended_movies": [
    {
      "rank":            1,
      "movie_name":      "...",
      "genre":           [...],
      "story":           "...",
      "mood":            [...],
      "cast":            [...],
      "industry":        "...",
      "year_of_release": 2000,
      "match_score":     0,
      "match_reason":    "<1 sentence explaining why this movie fits the query>"
    }
  ],
  "missing_tag_note": ""
}

## HARD CONSTRAINTS
1. Only use movies from the retrieved context — never invent one.
2. Copy field values exactly as stored — do not paraphrase movie_name or cast.
3. mood_flag = sensitive → mood safety filter is mandatory, no exceptions.
4. Always populate match_reason for every recommendation.
5. Always populate tag_coverage even if all fields are covered.
6. If fewer than 5 movies pass all filters, return however many do
   and set missing_tag_note to explain why others were excluded.
7. Output must be valid parseable JSON — no markdown fences, no extra text."""

    prompt = system_prompt + "\n" + context_str + f"\nUSER QUERY:\n{query}"
    response = llm.invoke(prompt)
    
    clean_json = response.content.strip()
    
    # Intelligently extract the JSON block even if the LLM added conversational text
    start_idx = clean_json.find('{')
    end_idx = clean_json.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        clean_json = clean_json[start_idx:end_idx+1]
        
    try:
        data = json_repair.loads(clean_json)
        if isinstance(data, str):
            # If it's still a string, it means the LLM returned conversational text without JSON
            return {"error": f"LLM refused to generate JSON. Raw response: {clean_json[:200]}", "raw_response": clean_json}
            
        data["original_story"] = query
        return data
    except Exception as e:
        return {"error": f"LLM Output completely corrupted. Error: {str(e)} | Raw Output: {clean_json[:200]}", "raw_response": clean_json}
