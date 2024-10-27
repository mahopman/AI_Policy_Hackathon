from openai import OpenAI
import streamlit as st
from risk_assessment import RiskAssessment
from risk_tree import RiskTree
import json
import os
from sample_prompts import sample_prompts_short, sample_prompts_long
from knowledge_graph_setup import KnowledgeGraph

st.set_page_config(layout="wide")
st.title("Chatbot with Adaptive Policy Ontology")

policy = st.selectbox(
    'What policy would you like the chatbot to adhere to?',
    (
        'NO VIOLENCE: Do not endorse or encourage any violent behaivor', 
        'NO ANIMAL VIOLENCE: Do not endorse or encourage any violent behaivor towards animals', 
        'NO FANTASY VIOLENCE: Do not endorse or encourage any violent behaivor even in a fantasy setting',))

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

    st.session_state.observer_responses.append(observer_response)
    st.session_state.ontology.add_user_input(
        text=prompt,
        inference_conclusion=json.loads(observer_response)["inference_conclusion"],
        policy_matched=json.loads(observer_response)["policy_matched"],
        risk_level=json.loads(observer_response)["risk_level"],
        target_type=json.loads(observer_response)["target_type"],
        real_or_fake=json.loads(observer_response)["real_or_fake"],
        reasoning_path=json.loads(observer_response)["reasoning_path"]
    )    
    
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
            {{
                "user_input": [user input], 
                "inference_conclusion": [conclusion of the user's intent], 
                "policy_matched": [(No violence, No animal violence, No fantasy violence)], 
                "risk_level": [(Low, Medium, High)]
                "target_type": [type of target or victim e.g. animal, person]
                "real_or_fake": [context of violence (real or fantasy)]
                "reasoning_path": [how you arrived at the conclusion]
            }}

            Consider carefully the ethical and legal implications of the action when assigning the Risk Level.

            Do not include any other text or explanation in your response. Only provide the json format above with your analysis."
        """
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

#def parse_risk_assessments(data):
#    assessments = []
#    for entry in data:
#        if entry == "No risk detected.":
#            continue
#        try:
#            parsed_entry = json.loads(entry)
#            assessment = RiskAssessment(
#                victim=parsed_entry["victim"],
#                violence_type=parsed_entry["violence_type"],
#                reality=parsed_entry["reality"],
#                risk_level=parsed_entry["risk_level"]
#            )
#            assessments.append(assessment)
#        except:
#            pass
#    return assessments

st.text(st.session_state.observer_responses)
#print(parse_risk_assessments(st.session_state.observer_responses))

#with col2:
#    risk_tree = RiskTree.convertRiskAssessmentsToTree(parse_risk_assessments(st.session_state.observer_responses))
#    risk_tree = RiskTree(risk_tree)
#    risk_tree.render()
#    risk_tree.export()
    
#    if risk_tree.root_nodes:
#        if os.path.exists("victim.png"):
#            st.image("victim.png")
#        if os.path.exists("violence_type.png"):
#            st.image("violence_type.png")
#        if os.path.exists("reality.png"):
#            st.image("reality.png")

with col2:
    html_str = st.session_state.ontology.visualize_graph()
    st.markdown(html_str, unsafe_allow_html=True)