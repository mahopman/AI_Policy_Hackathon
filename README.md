# Mapping Intent: Documenting Policy Adherence with Ontology Extraction

## Overview

This project addresses the AI policy challenge of governing agentic systems by making their decision-making processes more accessible. Our solution utilizes an adaptive policy ontology integrated into a chatbot to clearly visualize and analyze its decision-making process. By creating explicit mappings between user inputs, policy rules, and risk levels, our system enables better governance of AI agents by making their reasoning traceable and adjustable. This approach facilitates continuous policy refinement and could aid in detecting and mitigating harmful outcomes. Our results demonstrate this with the example of “tricking” an agent into giving violent advice by caveating the request saying it is for a “video game”. Indeed, the ontology clearly shows where the policy falls short. This approach could be scaled to provide more interpretable documentation of AI chatbot conversations, which policy advisers could directly access to inform their specifications. 

This project was developed as part of a [hackathon submission](https://www.apartresearch.com/project/mapping-intent-documenting-policy-adherence-with-ontology-extraction) for Apart Research.

## Features

- AI Chatbot Agent
- AI Observer Agent, extracts relevant policy and risk fields
- Ontology managed with neo4j
- Adaptive policy vizualization

## Usage

To run it locally:

1. Set up your environment variables in `.streamlit/secrets.toml`:
   - `OPENAI_API_KEY`: Your OpenAI API token
   - `NEO4J_URI`: URI to your neo4j space
   - `NEO4J_USER`: Your neo4j username
   - `NEO4J_PASSWORD`: Your neo4j password

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. Open your web browser and navigate to the provided local URL.

## Project Structure

- `app.py`: The main Streamlit application
- `agent_knowledge_graph_setup.py`: Contains KnowledgeGraph class and related functions
- `sample_prompts.py`: Lists sample prompts to run

## Technologies Used

- Streamlit
- OpenAI API
- neo4j
- OWL

## Authors

- Alejandra de Brunner
- Mia Hopman
- Jack Wittmayer

## Acknowledgments

Special thanks to Apart Research for their support and guidance. 
