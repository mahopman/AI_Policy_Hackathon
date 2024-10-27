from openai import OpenAI
import streamlit as st

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

        If the text contains anything that could pose a risk to the policy, you must respond using EXACTLY this format, replacing the text in brackets with your analysis:
        Victim: [Person, Object, or Animal]
        Violence Type: [Emotional, or Physical]
        Reality: [Fictional or Non-Fictional]
        Risk Level: [Low, Medium, or High]

        Consider carefully the ethical and legal implications of the action when assigning the Risk Level.

        Only provide the four lines above with your analysis if the text contains some risk. If there is no risk, DO NOT RESPOND. Do not include any other text or 
        explanation in your response. 
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

st.text(st.session_state.observer_responses)