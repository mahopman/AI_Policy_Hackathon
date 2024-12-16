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

        # tx.run("CREATE (:Policy_Rule {value: 'no violence'})")
        # tx.run("CREATE (:Policy_Rule {value: 'no animal violence'})")
        # tx.run("CREATE (:Policy_Rule {value: 'no fantasy violence'})")

        # tx.run("CREATE (:Risk_Level {value: 'low'})")
        # tx.run("CREATE (:Risk_Level {value: 'medium'})")
        # tx.run("CREATE (:Risk_Level {value: 'high'})")

        #print("Core nodes created successfully.")
        pass

    def add_user_input(self, fixed_attributes, var_attributes):
        with self.driver.session() as session:
            session.write_transaction(
                self.create_user_input, fixed_attributes, var_attributes
            )

    @staticmethod
    def create_user_input(tx, fixed_attributes, var_attributes):
        # for attribute in fixed_attributes.values():
        #     print(attribute.value)
        user_input_query = """
        CREATE (u:UserInput {value: $user_input})
        RETURN u
        """
        tx.run(user_input_query, user_input=fixed_attributes["user_input"].value[:100])

        violation_degree = fixed_attributes["violation_degree"].value.lower()
        policy_violation = fixed_attributes["policy_violation"].value.lower()
        inference_conclusion = fixed_attributes["inference_conclusion"].value
        reasoning_path = fixed_attributes["reasoning_path"].value
        inference_query = """
        MERGE (r:Violation_Degree {value: $violation_degree})
        MERGE (p:Policy_Violation {value: $policy_violation})
        CREATE (i:Inference {value: $inference_conclusion, reasoning: $reasoning_path})
        CREATE (r)-[:INFERRED_RISK]->(i)
        CREATE (p)-[:POLICY_MATCH]->(i)
        WITH i
        MATCH (u:UserInput {value: $user_input})
        CREATE (u)-[:INFERENCE]->(i)
        """
        #print("INFERENCE QUERY", inference_query)
        tx.run(inference_query, violation_degree=violation_degree, policy_violation=policy_violation, inference_conclusion=inference_conclusion, reasoning_path=reasoning_path, user_input=fixed_attributes["user_input"].value[:100])

        for attribute in var_attributes.values():
            if attribute.value == "":
                continue
            query = f"""
            MERGE (v:{attribute.name} {{value: $attribute_value}})
            WITH v
            MATCH (r:Violation_Degree {{value: $violation_degree}})
            CREATE (v)-[:RISKFACTORS]->(r)
            """
            #print(query)
            tx.run(query, attribute_value=attribute.value.lower(), violation_degree=violation_degree)

        #print("User input, inferences, and relationships created successfully.")

    def visualize_graph(self, filename, heading):
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", heading=heading)
        
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
            result = session.run("MATCH (n) RETURN elementId(n) AS id, labels(n) AS labels, n.value AS value, n.name AS name, n.text AS text, n.level AS level, n.context AS context, n.type AS type, n.conclusion AS conclusion")
            for record in result:
                #print(record)
                node_id = record["id"]
                labels = record["labels"]
                label = labels[0] 
                
                name = record["value"] or record["text"] or record["level"] or record["context"] or record["type"] or record["conclusion"] or label
                title = f"{label}: {name}"
                
                net.add_node(node_id, label=title, title=title, group=label)

            result = session.run("MATCH (a)-[r]->(b) RETURN elementId(a) AS source, elementId(b) AS target, type(r) AS type")
            for record in result:
                #print(record)
                net.add_edge(record["source"], record["target"], title=record["type"])

        net.write_html(filename)
        print(f"Graph visualization saved as {filename}")

        #if os.path.isfile(output_file):
        #    webbrowser.open("file://" + os.path.abspath(output_file))
        #else:
        #    print("Failed to open the visualization HTML file.")

if __name__ == "__main__":
    kg = KnowledgeGraph()

    kg.setup_graph()

    kg.add_user_input(
        text="How do I kill my dog?",
        inference_conclusion="User intends harm",
        policy_matched="No animal violence",
        violation_degree="High",
        target_type="pet",
        real_or_fake="real",
        reasoning_path="User identified as young; action classified as real intent"
    )

    kg.add_user_input(
        text="What are some ways to prank a friend?",
        inference_conclusion="User seeks harmless mischief",
        policy_matched="No violence",
        violation_degree="Low",
        target_type="person",
        real_or_fake="fantasy",
        reasoning_path="Action identified as prank and non-harmful"
    )

    kg.visualize_graph()

    kg.close()
