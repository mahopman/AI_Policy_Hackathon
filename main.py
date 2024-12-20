from knowledge_graph_setup import KnowledgeGraph
from observer import Observer
import pandas as pd
import json
from constants import fixed_attributes, var_attributes, developer_mode_prompt, parallel_universe_prompt, prompts
from chatbot import Chatbot
import os
from conversation import Conversation
import datetime
import random

#prompt_ids = [2, 13, 18, 27, 23, 39, 48, 58, 59, 56, 54, 55, 51]

if os.path.exists("prompts.parquet"):
    prompts_df = pd.read_parquet("prompts.parquet")
else:
    prompts_df = pd.read_parquet("hf://datasets/HuggingFaceH4/cai-conversation-harmless/data/train_sft-00000-of-00001-7f69edecc397f342.parquet")
    prompts_df.to_parquet("prompts.parquet")
prompt_ids = random.sample(range(0, len(prompts_df)), 10)
print("Prompt ids:", prompt_ids)
#prompts = prompts_df.iloc[prompt_ids]["prompt"].tolist()
prompts = open("selected_prompts.txt", "r").readlines()

jailbreak_prompt = parallel_universe_prompt

with open("policies.json", "r") as f:
    policies = json.load(f)

NUM_PROMPTS = 10
NUM_POLICIES = 1
CONVERSATION_LENGTH = 1
USE_PREGENERATED_USER_INPUT = False
USE_PREGENERATED_ASSISTANT_OUTPUT = False
CONVERSATION_TO_LOAD = "conversations/conversation_gpt3.5.txt"
pregenerated_conversation = Conversation(CONVERSATION_TO_LOAD)

def send_prompts_to_chatbot(prompts, policies, use_pregen_assistant, jailbreak_model):
    for policy in policies[1:NUM_POLICIES+1]:
        print("Starting run with the following policy")
        print(policy)
        kg = KnowledgeGraph()
        kg.setup_graph()
        multiprompt_conversation = Conversation()
        
        observer = Observer(policy["policy"], "gpt-4o-mini")
            # multiprompt_conversation.add_user_input(jailbreak_prompt)
            # multiprompt_conversation.add_assistant_response(chatbot_response)
        for prompt_id, prompt in enumerate(prompts[:NUM_PROMPTS]):
            if prompt_id % 1 == 0:
                print("Starting chatbot with fresh history...")
                chatbot = Chatbot(policy, temperature=0.0)
                if jailbreak_model:
                    print("Sending jailbreak prompt...")
                    chatbot_response = chatbot.get_response(jailbreak_prompt)
            observer_input = ""
            
            if not use_pregen_assistant:
                chatbot_response = chatbot.get_response(prompt)
                
            else:
                chatbot_response = pregenerated_conversation.get_assistant_response(prompt_id)
            
            multiprompt_conversation.add_user_input(prompt)
            multiprompt_conversation.add_assistant_response(chatbot_response)
            observer_input = multiprompt_conversation.get_conversation_at_steps([prompt_id])

            try:
                fixed_attributes, var_attributes = observer.extract_attributes(observer_input)
                print(f"OBSERVER RESPONSE {prompt_id}")
                for attribute in fixed_attributes.values():
                    print(f"{attribute.name}: {attribute.value}")
                for attribute in var_attributes.values():
                    print(f"{attribute.name}: {attribute.value}")
                print()
            
                kg.add_user_input(
                    fixed_attributes, var_attributes
                )
            except json.JSONDecodeError as e:
                print("Skipping prompt", prompt_id, "after failing to get observer response.")
                continue

    if not use_pregen_assistant:
        multiprompt_conversation.save_to_file(f"conversations/multiprompt_conversation_policy_{policy['id']}_{str(datetime.datetime.now())}")
    kg.visualize_graph(f"viz/KG_policy{policy['id']}.html", "Policy: " + policy["policy"])
    kg.close()

def have_long_conversation(policies, conversation_length, use_pregen_user=False, use_pregen_assistant=False):
    for policy in policies[1:NUM_POLICIES+1]:
        print("Starting run with the following policy")
        print(policy)
        kg = KnowledgeGraph()
        kg.setup_graph()
        new_conversation = Conversation()
        chatbot = Chatbot(policy, temperature=0.0)
        observer_input = ""
        
        for conversation_index in range(conversation_length):
            if not use_pregen_user:
                if conversation_index == 0:
                    print("Starting the conversation with the following prompt:")
                    print(prompt)
                if conversation_index > 0:
                    print()
                    print(observer_input)
                    prompt = input("Enter the next user input for the above conversation: ")
            else:
                prompt = pregenerated_conversation.get_user_input(conversation_index)
            if not use_pregen_assistant:
                chatbot_response = chatbot.get_response(prompt)
                
            else:
                chatbot_response = pregenerated_conversation.get_assistant_response(conversation_index)
            
            new_conversation.add_user_input(prompt)
            new_conversation.add_assistant_response(chatbot_response)
            observer_input = new_conversation.get_conversation_up_to_step(conversation_index)

            observer = Observer(policy["policy"], "gpt-4o-mini")
            fixed_attributes, var_attributes = observer.extract_attributes(observer_input)
            print(f"OBSERVER RESPONSE {conversation_index}")
            for attribute in fixed_attributes.values():
                print(f"{attribute.name}: {attribute.value}")
            for attribute in var_attributes.values():
                print(f"{attribute.name}: {attribute.value}")
            print()
        
            kg.add_user_input(
                fixed_attributes, var_attributes
            )

            kg.visualize_graph(f"viz/KG_policy{policy['id']}_pass{conversation_index}.html", "Policy: " + policy["policy"])
        
        new_conversation.save_to_file(f"conversations/conversation_policy_{policy['id']}_{str(datetime.datetime.now())}")
    kg.close()

def main():
    send_prompts_to_chatbot(prompts, policies, False, jailbreak_model=True)
    #have_long_conversation(policies, 7, True, False)

if __name__ == "__main__":
    main()

