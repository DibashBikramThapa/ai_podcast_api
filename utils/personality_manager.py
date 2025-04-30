import json
import os
from typing import Dict


class PersonalityManager:
    """Manager for LLM personalities"""
    
    def __init__(self, file_path="personalities.json"):
        self.file_path = file_path
        self.default_personalities = {
            "deepseek-chat": "You are DeepSeek, an analytical and thoughtful AI. You consider multiple perspectives before responding and excel at technical discussions.",
            "chatgpt-4o-latest": "You are ChatGPT, a helpful and versatile AI. You're good at explaining complex concepts clearly and providing balanced viewpoints.",
            "google/gemini-2.0-flash": "You are Gemini, an insightful and creative AI. You make unexpected connections between ideas and offer unique perspectives.",
            "x-ai/grok-3-beta": "You are Grok, a witty and straightforward AI. You're not afraid to be humorous and direct in your responses.",
            "claude-3-sonnet-20240229": "You are Claude, an empathetic and thoughtful AI. You excel at understanding nuance and the human aspects of any topic.",
            "gpt-4o": "You are GPT-4o, a knowledgeable and precise AI. You provide comprehensive and well-structured responses based on extensive knowledge."
        }
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create personalities file if it doesn't exist"""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump(self.default_personalities, f, indent=2)
    
    def get_personalities(self) -> Dict[str, str]:
        """Get all personality prompts"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid, return defaults
            return self.default_personalities
    
    def get_personality(self, model_id: str) -> str:
        """Get personality prompt for a specific model"""
        personalities = self.get_personalities()
        return personalities.get(model_id, self.default_personalities.get(model_id, "You are a helpful AI assistant."))
    
    def update_personality(self, model_id: str, personality: str) -> bool:
        """Update personality for a specific model"""
        personalities = self.get_personalities()
        personalities[model_id] = personality
        return self._save_personalities(personalities)
    
    def update_all_personalities(self, personalities: Dict[str, str]) -> bool:
        """Update all personalities at once"""
        return self._save_personalities(personalities)
    
    def reset_to_defaults(self) -> bool:
        """Reset all personalities to defaults"""
        return self._save_personalities(self.default_personalities)
    
    def _save_personalities(self, personalities: Dict[str, str]) -> bool:
        """Save personalities to file"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(personalities, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving personalities: {e}")
            return False 