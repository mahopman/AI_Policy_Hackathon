from neo4j import GraphDatabase
import streamlit as st
from pyvis.network import Network
import webbrowser
import os

class KnowledgeGraph:

    def __init__(self):
        uri = st.secrets["NEO4J_URI"]
        user = st.secrets["NEO4J_USER"]
        password = st.secrets["NEO4J_PASSWORD"]
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def setup_graph(self):
        with self.driver.session() as session:
            session.write_transaction(self.create_core_nodes)

    @staticmethod
    def create_core_nodes(tx):
        tx.run("MATCH (n) DETACH DELETE n")

        tx.run("CREATE (:Policy_Rule {name: 'No violence'})")
        tx.run("CREATE (:Policy_Rule {name: 'No animal violence'})")
        tx.run("CREATE (:Policy_Rule {name: 'No fantasy violence'})")

        tx.run("CREATE (:Risk_Level {level: 'Low'})")
        tx.run("CREATE (:Risk_Level {level: 'Medium'})")
        tx.run("CREATE (:Risk_Level {level: 'High'})")

        tx.run("CREATE (:Target_Type {type: 'pet'})")
        tx.run("CREATE (:Target_Type {type: 'person'})")

        tx.run("CREATE (:RealOrFake {context: 'real'})")
        tx.run("CREATE (:RealOrFake {context: 'fantasy'})")

        print("Core nodes created successfully.")

    def add_user_input(self, text, inference_conclusion, policy_matched, risk_level, target_type, real_or_fake, reasoning_path=""):
        with self.driver.session() as session:
            session.write_transaction(
                self.create_user_input, 
                text, inference_conclusion, policy_matched, 
                risk_level, target_type, real_or_fake, reasoning_path
            )

    @staticmethod
    def create_user_input(tx, text, inference_conclusion, policy_matched, risk_level, target_type, real_or_fake, reasoning_path):
        user_input_query = """
        CREATE (u:UserInput {text: $text})
        RETURN u
        """
        tx.run(user_input_query, text=text[:100])

        inference_query = """
        MATCH (r:Risk_Level {level: $risk_level}), (p:Policy_Rule {name: $policy_matched})
        CREATE (i:Inference {conclusion: $inference_conclusion, reasoning_path: $reasoning_path})
        CREATE (r)-[:INFERRED_RISK]->(i)
        CREATE (p)-[:POLICY_MATCH]->(i)
        WITH i
        MATCH (u:UserInput {text: $text})
        CREATE (u)-[:INFERENCE]->(i)
        """
        tx.run(inference_query, risk_level=risk_level, policy_matched=policy_matched, inference_conclusion=inference_conclusion, reasoning_path=reasoning_path, text=text[:100])

        tx.run("""
        MATCH (t:Target_Type {type: $target_type}), (rf:RealOrFake {context: $real_or_fake}), (r:Risk_Level {level: $risk_level})
        CREATE (t)-[:RISKFACTORS]->(r)
        CREATE (rf)-[:RISKFACTORS]->(r)
        """, target_type=target_type, real_or_fake=real_or_fake, risk_level=risk_level)

        print("User input, inferences, and relationships created successfully.")

    def visualize_graph(self):
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        
        net.barnes_hut(gravity=-3000, central_gravity=0.2, spring_length=150, spring_strength=0.02)
        net.set_options("""
        var options = {
          "nodes": {
            "font": {
              "size": 16,
              "face": "arial",
              "color": "white",
              "strokeWidth": 2
            }
          },
          "edges": {
            "arrows": {"to": { "enabled": true, "scaleFactor": 1 }},
            "color": {"inherit": "both"},
            "smooth": true
          },
          "physics": {
            "enabled": true,
            "solver": "barnesHut",
            "barnesHut": {
              "gravitationalConstant": -20000,
              "centralGravity": 0.04,
              "springLength": 200,
              "springConstant": 0.01,
              "damping": 0.9
            },
            "minVelocity": 0.75
          }
        }
        """)

        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN elementId(n) AS id, labels(n) AS labels, n.name AS name, n.text AS text, n.level AS level, n.context AS context, n.type AS type, n.conclusion AS conclusion")
            for record in result:
                node_id = record["id"]
                labels = record["labels"]
                label = labels[0] 
                
                name = record["name"] or record["text"] or record["level"] or record["context"] or record["type"] or record["conclusion"] or label
                title = f"{label}: {name}"
                
                net.add_node(node_id, label=title, title=title, group=label)

            result = session.run("MATCH (a)-[r]->(b) RETURN elementId(a) AS source, elementId(b) AS target, type(r) AS type")
            for record in result:
                net.add_edge(record["source"], record["target"], title=record["type"])

        output_file = "knowledge_graph_visualization.html"
        net.write_html(output_file)
        print(f"Graph visualization saved as {output_file}")

        if os.path.isfile(output_file):
            webbrowser.open("file://" + os.path.abspath(output_file))
        else:
            print("Failed to open the visualization HTML file.")

if __name__ == "__main__":
    kg = KnowledgeGraph()

    kg.setup_graph()

    kg.add_user_input(
        text="How do I kill my dog?",
        inference_conclusion="User intends harm",
        policy_matched="No animal violence",
        risk_level="High",
        target_type="pet",
        real_or_fake="real",
        reasoning_path="User identified as young; action classified as real intent"
    )

    kg.add_user_input(
        text="What are some ways to prank a friend?",
        inference_conclusion="User seeks harmless mischief",
        policy_matched="No violence",
        risk_level="Low",
        target_type="person",
        real_or_fake="fantasy",
        reasoning_path="Action identified as prank and non-harmful"
    )

    kg.visualize_graph()

    kg.close()
