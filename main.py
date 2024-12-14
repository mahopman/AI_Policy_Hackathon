from knowledge_graph_setup import KnowledgeGraph
from observer import Observer
import pandas as pd
import json

prompt_ids = [2, 13, 18, 27, 23, 39, 48, 58, 59, 56, 54, 55, 51]
prompts_df = pd.read_parquet("hf://datasets/HuggingFaceH4/cai-conversation-harmless/data/train_sft-00000-of-00001-7f69edecc397f342.parquet")
prompts = prompts_df.iloc[prompt_ids]["prompt"].tolist()

with open("policies.json", "r") as f:
    policies = json.load(f)

def main():
    
    for policy in policies:

        for prompt_id, prompt in enumerate(prompts):
            observer = Observer(policy["policy"])
            attributes = observer.extract_attributes(prompt)
            attributes = json.loads(attributes)
            print(attributes)

            kg = KnowledgeGraph()
            kg.setup_graph()

            kg.add_user_input(
                text=prompt,
                inference_conclusion=attributes["inference_conclusion"],
                policy_matched=policy["policy"],
                risk_level=attributes["risk_level"].lower(),
                target_type=attributes["target_type"].lower(),
                real_or_fake=attributes["real_or_fake"].lower(),
                reasoning_path=attributes["reasoning_path"]
                )

            kg.visualize_graph(f"KG_policy{policy['id']}_prompt{prompt_id}.html")

            kg.close()

if __name__ == "__main__":
    main()

