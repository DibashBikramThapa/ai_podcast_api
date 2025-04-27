from enum import Enum
from utils import settings


class AI_API_KEYS(Enum):
    DEEPSEEK=settings.DEEPSEEK
    CHATGPT=settings.CHATGPT
    GEMINI=settings.GEMINI
    GROK=settings.GROK
    CLAUDE=settings.CLAUDE
    AI_ML=settings.AI_ML


class AI_Model(Enum):
    DEEPSEEK="deepseek-chat"
    CHATGPT="chatgpt-4o-latest"
    GEMINI="google/gemini-2.0-flash"
    GROK="x-ai/grok-3-beta"
    CLAUDE="claude-3-sonnet-20240229"
    AI_ML="gpt-4o"
