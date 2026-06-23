from dotenv import load_dotenv
import os

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# The single model used everywhere across the agent.
MODEL = os.getenv("MODEL", "llama-3.1-8b-instant")

# Groq's OpenAI-compatible endpoint.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
KNOWLEDGE_FILE = "sable_knowledge.json"