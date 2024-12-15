from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

class Chatbot:
    def __init__(self, policy, model="gpt-3.5-turbo"):
        self.policy = policy
        self.openai_model = model
        self.message_history = [{"role": "system", "content": f"Respond to the best of your ability and adhere to the following policy: {self.policy}"}]

    def conversation_to_input(self):
        full_conversation = ""
        for message in self.message_history[1:]:
            if message["role"] == "user":
                full_conversation += "USER: " + message["content"] + "\n"
            elif message["role"] == "assistant":
                full_conversation += "ASSISTANT: " + message["content"] + "\n"
        return full_conversation 

    def get_response(self, prompt):
        self.message_history.append({"role": "user", "content": prompt})
        response_message = client.chat.completions.create(
            model=self.openai_model,
            messages=self.message_history,
        ).choices[0].message.content

        self.message_history.append({"role": "assistant", "content": response_message})
        return response_message