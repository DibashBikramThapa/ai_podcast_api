import os
from dotenv import load_dotenv

load_dotenv()


DEEPSEEK=os.getenv('DEEPSEEK_API')
CHATGPT=os.getenv('DEEPSEEK_API')
GEMINI=os.getenv('GEMINIAPI')
GROK=os.getenv('GROK_API')
CLAUDE=os.getenv('CLAUDE_API')
AI_ML=os.getenv('AI_ML_API')

HOST = os.getenv('HOST')

origins = [
    "http://localhost:3000",
    "http://localhost",
    os.getenv('FRONTEND_URL'),  # Add your frontend domain
    "http://127.0.0.1", #if you are using IP address
    "http://127.0.0.1:3000",
]