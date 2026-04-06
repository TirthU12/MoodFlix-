import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    max_tokens=3000,
    temperature=0.0
)

response = llm.invoke("Say hello world in a JSON object like {'msg': 'hello world'}")
print("LLM RESPONSE CONTENT:")
print(repr(response.content))
