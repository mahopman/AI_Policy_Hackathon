from knowledge_graph_setup import KnowledgeGraph
from observer import Observer
import pandas as pd
import json
from constants import fixed_attributes, var_attributes, developer_mode_prompt, parallel_universe_prompt
from chatbot import Chatbot
import os
from conversation import Conversation
import datetime

prompt_ids = [2, 13, 18, 27, 23, 39, 48, 58, 59, 56, 54, 55, 51]
#prompt_ids = [1]
if os.path.exists("prompts.parquet"):
    prompts_df = pd.read_parquet("prompts.parquet")
else:
    prompts_df = pd.read_parquet("hf://datasets/HuggingFaceH4/cai-conversation-harmless/data/train_sft-00000-of-00001-7f69edecc397f342.parquet")
    prompts_df.to_parquet("prompts.parquet")
prompts = prompts_df.iloc[prompt_ids]["prompt"].tolist()

prompts = [parallel_universe_prompt]

with open("policies.json", "r") as f:
    policies = json.load(f)

NUM_PROMPTS = 1
NUM_POLICIES = 1
CONVERSATION_LENGTH = 5
USE_PREGENERATED_USER_INPUT = True
USE_PREGENERATED_ASSISTANT_OUTPUT = False
CONVERSATION_TO_LOAD = "conversation.txt"
pregenerated_conversation = Conversation(CONVERSATION_TO_LOAD)

def main():

    for policy in policies[:NUM_PROMPTS]:
        print("Starting run with the following policy")
        print(policy)
        for prompt_id, prompt in enumerate(prompts[:NUM_POLICIES]):
            print("Starting the conversation with the following prompt:")
            print(prompt)
            new_conversation = Conversation()
            chatbot = Chatbot(policy)
            observer_input = ""
            kg = KnowledgeGraph()
            kg.setup_graph()
            for conversation_index in range(CONVERSATION_LENGTH):
                if not USE_PREGENERATED_USER_INPUT:
                    if conversation_index > 0:
                        print()
                        print(observer_input)
                        prompt = input("Enter the next user input for the above conversation: ")
                else:
                    prompt = pregenerated_conversation.get_user_input(conversation_index)
                if not USE_PREGENERATED_ASSISTANT_OUTPUT:
                    chatbot_response = chatbot.get_response(prompt)
                    
                else:
                    chatbot_response = pregenerated_conversation.get_assistant_response(conversation_index)
                print()
                print("CHATBOT RESPONSE:", chatbot_response)
                new_conversation.add_user_input(prompt)
                new_conversation.add_assistant_response(chatbot_response)
                observer_input = new_conversation.get_conversation_at_step(conversation_index)

                observer = Observer(policy["policy"])
                fixed_attributes, var_attributes = observer.extract_attributes(observer_input)
                print("OBSERVER RESPONSE")
                for attribute in fixed_attributes.values():
                    print(f"{attribute.name}: {attribute.value}")
                for attribute in var_attributes.values():
                    print(f"{attribute.name}: {attribute.value}")
                print()
            
                kg.add_user_input(
                    fixed_attributes, var_attributes
                )

                kg.visualize_graph(f"viz/KG_policy{policy['id']}_prompt{prompt_id}_pass{conversation_index}.html")
            new_conversation.save_to_file(f"conversations/conversation_policy_{policy['id']}_{str(datetime.datetime.now())}")
            kg.close()

if __name__ == "__main__":
    main()

