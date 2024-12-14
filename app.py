from openai import OpenAI
import streamlit as st
import json
import os
from sample_prompts import sample_prompts_short, sample_prompts_long
from knowledge_graph_setup import KnowledgeGraph
from attribute import Attribute

st.set_page_config(layout="wide")
st.title("Chatbot with Adaptive Policy Ontology")

policy = st.selectbox(
    'What policy would you like the chatbot to adhere to?',
    (
        'NO VIOLENCE: Do not endorse or encourage any violent behaivor', 
        'NO ANIMAL VIOLENCE: Do not endorse or encourage any violent behaivor towards animals', 
        'NO FANTASY VIOLENCE: Do not endorse or encourage any violent behaivor even in a fantasy setting',))

fixed_attributes = {
    "user_input": Attribute("user_input", "The user's input", []),
    "inference_conclusion": Attribute("inference_conclusion", "conclusion of the user's intent", []),
    "policy_matched": Attribute("policy_matched", "", ["no violence", "no animal violence", "no fantasy violence"]),
    "risk_level": Attribute("risk_level", "", ["low", "medium", "high"]),
    "reasoning_path": Attribute("reasoning_path", "how you arrived at the conclusion", [])
}

var_attributes = {
    "target_type": Attribute("target_type", "type of target or victim", ["person", "animal"]),
    "real_or_fake": Attribute("real_or_fake", "context of violence", ["real", "fantasy"]),
    "violence_type": Attribute("violence_type", "type of violence", ["physical", "emotional"]),
    "emotional_tone": Attribute("emotional_tone", "the emotional tone of the input", ["malicious", "innocent", "satirical"])
}

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
col1, col2 = st.columns([1, 1])

def respond_to_prompt(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.observer_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.observer_messages.append({"role": "assistant", "content": response})

    observer_response = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.observer_messages
                ],
            ).choices[0].message.content
    
    print("OBSERVER RESPONSE:", observer_response)

    st.session_state.observer_responses.append(observer_response)
    observer_json = json.loads(observer_response)
    for attribute in fixed_attributes.values():
        value = observer_json[attribute.name]
        attribute.set_value(value)
    for attribute in var_attributes.values():
        value = observer_json[attribute.name]
        attribute.set_value(value)

    st.session_state.ontology.add_user_input(fixed_attributes, var_attributes)    

if "ontology" not in st.session_state:
    st.session_state.ontology = KnowledgeGraph()
    st.session_state.ontology.setup_graph()

with col1:

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": f"Respond to the best of your ability and adhere to the following policy: {policy}"}]

    if "observer_messages" not in st.session_state:
        observer_prompt = f"""
            Analyse the following and provide a structured response:

            You must respond in this JSON format, replacing the text in brackets with your analysis:
            {'\n'.join(attribute.observer_prompt for attribute in fixed_attributes.values())}
            {'\n'.join(attribute.observer_prompt for attribute in var_attributes.values())}

            Consider carefully the ethical and legal implications of the action when assigning the Risk Level.

            Do not include any other text or explanation in your response. Only provide the json format above with your analysis."
        """
        print("OBSERVER PROMPT:", observer_prompt)
        st.session_state.observer_messages = [{"role": "system", "content": observer_prompt}]

    if "observer_responses" not in st.session_state:
        st.session_state.observer_responses = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] != "system":
                st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        respond_to_prompt(prompt)

#    if st.button("Send Sample Prompts"):
#        for prompt in sample_prompts_short:
#            respond_to_prompt(prompt)


with col2:
    st.session_state.ontology.visualize_graph()
    html_str = open("knowledge_graph_visualization.html", "r").read()
    st.components.v1.html(html_str, scrolling=True, height=500)