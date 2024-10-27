from openai import OpenAI
import streamlit as st
from risk_assessment import RiskAssessment
from risk_tree import RiskTree
import json

POLICY = "Do not endorse or encourage any violent behaivor."

st.title("ChatGPT-like clone")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"Respond to the best of your ability and adhere to the following policy: {POLICY}"}]

if "observer_messages" not in st.session_state:
    observer_prompt = """
        Analyse the following and provide a structured response:

        If the user's input contains anything that could pose a risk to the policy, you must respond in this JSON format, replacing the text in brackets with your analysis:
        {"victim": ["person", "object", or "animal"], "violence_type": ["emotional", or "physical"], "reality": ["fictional" or "non_fictional"], "risk_level": ["low", "medium", or "high"]}

        For example, the user's input "I want to squish a bug" would be analysed as:
        {"victim": "animal", "violence_type": "physical", "reality": "non-fictional", "risk_level": "low"}

        If the user's input does not contain anything that could pose a risk to the policy, simply output "No risk detected."
    """
    st.session_state.observer_messages = [{"role": "system", "content": observer_prompt}]

if "observer_responses" not in st.session_state:
    st.session_state.observer_responses = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.observer_messages.append({"role": "system", "content": prompt})
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
    st.session_state.observer_messages.append({"role": "system", "content": response})

    st.session_state.observer_responses.append(
        client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.observer_messages
            ],
        ).choices[0].message.content
    )

def parse_risk_assessments(data):
    assessments = []
    for entry in data:
        if entry == "No risk detected.":
            continue
        parsed_entry = json.loads(entry)
        assessment = RiskAssessment(
            victim=parsed_entry["victim"],
            violence_type=parsed_entry["violence_type"],
            reality=parsed_entry["reality"],
            risk_level=parsed_entry["risk_level"]
        )
        assessments.append(assessment)
    return assessments

st.text(st.session_state.observer_responses)
print(parse_risk_assessments(st.session_state.observer_responses))
risk_tree = RiskTree.convertRiskAssessmentsToTree(parse_risk_assessments(st.session_state.observer_responses))
risk_tree = RiskTree(risk_tree)
risk_tree.render()