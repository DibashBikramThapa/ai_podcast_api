from openai import OpenAI
import html

from utils.enum import AI_API_KEYS, AI_Model
from utils.settings import HOST

base_url = f"{HOST}/v1"
api_key = AI_API_KEYS.AI_ML.value
api = OpenAI(api_key=api_key, base_url=base_url)

# System prompts
summarizer_system_prompt = """
You are a skilled summarizer and integrator of information. Your task is to:
1. Combine the different AI responses into a comprehensive, well-structured answer
2. Highlight key points where the AIs agree or disagree
3. Format your response as HTML with proper headings, paragraphs, and lists for readability. Start from <div> tag.
4. Include all major insights without unnecessary repetition
5. Make sure the summary is balanced and represents all the perspectives provided
6. Most important, your response should only contain HTML no extra texts
"""

individual_system_prompt = "You are a helpful, knowledgeable AI assistant. Provide a clear, concise, and informative response to the user's question or topic."


class AI_Summarizer:
    """Class to handle getting individual LLM responses and combining them with Gemini"""

    def __init__(self, payload: dict):
        self.user_prompt = payload["user_prompt"]

    def get_individual_response(self, model: AI_Model):
        """Get a response from a single LLM model"""
        messages = [
            {"role": "system", "content": individual_system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]

        # Special handling for Claude
        if model == AI_Model.CLAUDE:
            new_msg = []
            user_msg = {
                "role": "user",
                "content": f"{individual_system_prompt}\n\n{self.user_prompt}",
            }
            new_msg.append(user_msg)
        else:
            new_msg = messages

        try:
            completion = api.chat.completions.create(
                model=model.value,
                messages=new_msg,
                max_tokens=500,
            )
            resp = completion.choices[0].message.content
        except Exception as e:
            print(f"Error with {model.value}: {e}")
            resp = f"[Unable to get response from {model.value}]"

        return resp

    def combine_responses(self, responses: dict):
        """Use Gemini to combine all the individual responses"""
        # Format the responses for the combined prompt
        combined_input = f"Topic/Question: {self.user_prompt}\n\n"
        combined_input += "Here are the responses from different AI models:\n\n"

        for model, response in responses.items():
            model_name = self.get_model_display_name(model)
            combined_input += f"--- {model_name} Response ---\n{response}\n\n"

        combined_input += "Please combine these responses into a comprehensive answer following the instructions in your system prompt."

        messages = [
            {"role": "system", "content": summarizer_system_prompt},
            {"role": "user", "content": combined_input},
        ]

        try:
            # Use Gemini for the combination
            completion = api.chat.completions.create(
                model=AI_Model.GEMINI.value,
                messages=messages,
                max_tokens=1000,
            )
            combined_resp = completion.choices[0].message.content
            combined_resp = combined_resp.strip()
            combined_resp = combined_resp.replace("```html", "").replace("```", "")

            # Ensure the response is properly formatted HTML
            backslash_n = "\n"
            if not combined_resp.strip().startswith("<"):
                combined_resp = f"<div>{html.escape(combined_resp).replace(backslash_n, '<br>')}</div>"

        except Exception as e:
            print(f"Error combining responses: {e}")
            combined_resp = "<p>Error generating combined response. Please view individual responses instead.</p>"

        return combined_resp

    def get_model_display_name(self, model_value: str):
        """Convert model ID to display name"""
        model_names = {
            "deepseek-chat": "DeepSeek",
            "chatgpt-4o-latest": "ChatGPT",
            "google/gemini-2.0-flash": "Gemini",
            "x-ai/grok-3-beta": "Grok",
            "claude-3-sonnet-20240229": "Claude",
            "gpt-4o": "GPT-4o",
        }
        return model_names.get(model_value, model_value)

    def start(self):
        """Get responses from all LLMs and create a combined response"""
        individual_responses = {}

        # Get responses from each model
        for model in AI_Model:
            response = self.get_individual_response(model)
            individual_responses[model.value] = response

        # Combine the responses using Gemini
        combined_response = self.combine_responses(individual_responses)

        return individual_responses, combined_response
