from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

class Observer:
    def __init__(self, policy, model="gpt-3.5-turbo"):
        
        self.observer_prompt = f"""
            Analyse the following and provide a structured response, based on the following policy:

            {policy}

            You must respond in this JSON format, replacing the text in brackets with your analysis:
            {{
                "user_input": [user input], 
                "inference_conclusion": [conclusion of the user's intent],
                "risk_level": [(Low, Medium, High)]
                "target_type": [type of target or victim e.g. animal, person]
                "real_or_fake": [context of violence (real or fantasy)]
                "reasoning_path": [how you arrived at the conclusion]
            }}

            Consider carefully the ethical and legal implications of the action when assigning the Risk Level.

            Do not include any other text or explanation in your response. Only provide the json format above with your analysis."
        """ 

        self.observer_messages = [{"role": "system", "content": self.observer_prompt}]
        self.observer_responses = []
        self.openai_model = model

    def extract_attributes(self, prompt):
        # Needs to have conversation history set up?
        self.observer_messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.openai_model,
            messages=self.observer_messages,
        ).choices[0].message.content
    
        self.observer_responses.append(response)
        return response
    

