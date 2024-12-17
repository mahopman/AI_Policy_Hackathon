from openai import OpenAI
import replicate
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

class Chatbot:
    def __init__(self, policy, api="openai", model="gpt-3.5-turbo"):
        self.policy = policy
        self.api = api
        self.model = model
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
        if self.api == "openai":
            response_message = openai_client.chat.completions.create(
                model=self.model,
                messages=self.message_history,
            ).choices[0].message.content
            self.message_history.append({"role": "assistant", "content": response_message})
        else:
            conversation = f"You are a helpful assistant. You do not respond as 'USER' or pretend to be 'USER'. You only respond once as 'ASSISTANT'. Adhere to the following policy: {self.policy}\n"
            conversation += self.conversation_to_input()
            conversation += "ASSISTANT: "
            response_message = ""
            for token in replicate.stream(
                self.model,
                input={"prompt": conversation}
            ):
                print(str(token), end="")
                response_message += str(token)

        self.message_history.append({"role": "assistant", "content": response_message})
        return response_message