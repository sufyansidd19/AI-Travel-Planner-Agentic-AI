import os 
from urllib.parse import quote_plus
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


GROQ_API_KEY=os.getenv("GROQ_API_KEY")
AVIATION_STACK_API_KEY=os.getenv("AVIATION_STACK_API_KEY")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY=os.getenv("OPENWEATHER_API_KEY")
DATABASE_URL=(
    f"postgresql://postgres:{quote_plus(os.getenv('POSTGRES_PASS', ''))}"
    f"@localhost:{int(os.getenv('POSTGRES_PORT', 5432))}/langraph_memory_demo"
)

def get_llm():
    return ChatGroq(model=os.getenv("GROQ_MODEL","llama-3.3-70b-versatile"))