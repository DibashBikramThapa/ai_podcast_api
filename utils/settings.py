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