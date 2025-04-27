from openai import OpenAI

from utils.enum import AI_API_KEYS, AI_Model
from utils.settings import HOST

base_url = f"{HOST}/v1"
api_key = AI_API_KEYS.AI_ML.value
system_prompt = "You are a guest in ai text podcast. Provide your opinion in user and other ai guest's opinions."
api = OpenAI(api_key=api_key, base_url=base_url)


class AI_Podcast:

    def __init__(self, payload: dict, model: str):
        self.user_prompt = payload['user_prompt']
        self.prev_prompt = payload.get('prev_prompt')
        try:
            key = AI_Model(model)
        except ValueError:
            raise ValueError("Invalid ai model.")
        self.model = key

    def execute(self):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]
        if self.prev_prompt:
            assistant_msg = [{"role": "assistant", "content": each} for each in self.prev_prompt]
            messages.extend(assistant_msg)
        if self.model == AI_Model.CLAUDE:
            new_msg = []
            to_add = ''
            for each in messages:
                if each['role'] == 'user':
                    each['content'] = f'{to_add}\n\n' + each['content']
                    new_msg.append(each)
                elif each['role'] != "system":
                    new_msg.append(each)
                else:
                    to_add = each['content']
        else:
            new_msg = messages
        new_msg = list(filter(lambda x: x['content'], new_msg))
        try:
            completion = api.chat.completions.create(
                            model=self.model.value,
                            messages=new_msg,
                            max_tokens=256,
                    )
            resp = completion.choices[0].message.content
        except Exception as e:
            print(f'error in ai model completion: {e}')
            resp = ''
        return resp

    def start(self):
        model_podcast_resp = {self.model.value: self.execute()}
        for i, model  in enumerate(AI_Model):
            if model not in  [self.model]:
                payload = {
                            "user_prompt" : self.user_prompt
                            }
                payload['prev_prompt'] = list(model_podcast_resp.values())

                model_podcast_resp[model.value] = AI_Podcast(payload=payload, model=model.value).execute()
        return model_podcast_resp


