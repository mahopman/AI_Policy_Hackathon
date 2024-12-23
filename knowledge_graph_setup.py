from neo4j import GraphDatabase
import streamlit as st
from pyvis.network import Network
from attribute_storage import divide_into_fixed_and_var
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
        user_input = fixed_attributes["user_input"].value[:100]
        user_input_query = """
        CREATE (u:UserInput {value: $user_input})
        RETURN u
        """
        tx.run(user_input_query, user_input=user_input)

        assistant_response = fixed_attributes["assistant_response"].value[:100]
        assistant_intent = fixed_attributes["assistant_intent"].value
        assistant_response_query = """
        CREATE (a:AssistantResponse {value: $assistant_response, details: $assistant_intent})
        WITH a
        MATCH (u:UserInput {value:$user_input})
        CREATE (a)-[:RESPONDS_TO]->(u)
        """
        tx.run(assistant_response_query, user_input=user_input, assistant_response=assistant_response, assistant_intent=assistant_intent)

        violation_degree = fixed_attributes["violation_degree"].value.lower()
        policy_violation = fixed_attributes["policy_violation"].value.lower()
        reasoning_path = fixed_attributes["reasoning_path"].value

        inference_query = """
        // Merge or find the Violation_Degree node
        MERGE (r:Violation_Degree {value: $violation_degree})
        ON CREATE SET r.occurrence = 1
        ON MATCH SET r.occurrence = r.occurrence + 1

        // Merge or find the Policy_Violation node
        MERGE (p:Policy_Violation {value: $policy_violation})
        ON CREATE SET p.occurrence = 1
        ON MATCH SET p.occurrence = p.occurrence + 1

        // Find the AssistantResponse node and create relationships
        WITH p, r
        MATCH (a:AssistantResponse {value: $assistant_response})
        CREATE (r)-[:INFERRED_RISK]->(a)
        CREATE (a)-[:VIOLATES]->(p)

        // Create DEGREE relationship between Policy_Violation and Violation_Degree
        WITH p, r
        CREATE (p)-[:DEGREE]->(r)
        """


        #print("INFERENCE QUERY", inference_query)
        tx.run(inference_query, violation_degree=violation_degree, policy_violation=policy_violation, assistant_intent=assistant_intent, reasoning_path=reasoning_path, assistant_response=assistant_response)

        for attribute in var_attributes.values():
            if attribute.value == "":
                continue
            query = f"""
            // Merge or find the node for the attribute
            MERGE (v:{attribute.name} {{value: $attribute_value}})
            ON CREATE SET v.occurrence = 1
            ON MATCH SET v.occurrence = v.occurrence + 1

            // Create the relationship to the Violation_Degree node
            WITH v
            MATCH (r:Violation_Degree {{value: $violation_degree}})
            CREATE (v)-[:RISKFACTORS]->(r)
            """
            tx.run(query, attribute_value=attribute.value.lower(), violation_degree=violation_degree)



        #print("User input, inferences, and relationships created successfully.")

    def visualize_graph(self, filename, heading):
        net = Network(height="750px", width="100%", bgcolor="#1e1e2e", font_color="white", heading=heading)

        # Adjust Barnes-Hut physics for better spacing and clustering
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=250, spring_strength=0.05, damping=0.5)

        # Set improved options
        net.set_options("""
        var options = {
        "nodes": {
            "shape": "dot",
            "scaling": {
            "min": 10,
            "max": 30,
            "label": {
                "enabled": true,
                "min": 14,
                "max": 20,
                "maxVisible": 10
            }
            },
            "font": {
            "size": 16,
            "face": "verdana",
            "color": "white"
            },
            "color": {
            "background": "#6a4c93",
            "border": "#ffffff",
            "highlight": {
                "background": "#ff5e57",
                "border": "#ffffff"
            }
            },
            "borderWidth": 2
        },
        "edges": {
            "arrows": {"to": { "enabled": true, "scaleFactor": 1.2 }},
            "color": {
            "color": "#bababa",
            "highlight": "#ff5e57",
            "inherit": false
            },
            "smooth": {
            "enabled": true,
            "type": "dynamic"
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 200,
            "navigationButtons": true,
            "zoomView": true
        },
        "physics": {
            "enabled": true,
            "solver": "barnesHut",
            "barnesHut": {
            "gravitationalConstant": -20000,
            "centralGravity": 0.4,
            "springLength": 250,
            "springConstant": 0.02,
            "damping": 0.9
            },
            "minVelocity": 0.5,
            "timestep": 0.5
        }
        }
        """)

        with self.driver.session() as session:
            # Retrieve all nodes and their properties
            result = session.run(
                "MATCH (n) RETURN elementId(n) AS id, labels(n) AS labels, n.value AS value, n.details AS details, n.occurrence AS occurrence"
            )

            # Collect occurrences to calculate the size range
            nodes = []
            max_occurrence = 0
            for record in result:
                nodes.append(record)
                if record["occurrence"] is not None:
                    max_occurrence = max(max_occurrence, int(record["occurrence"]))

            # Define size range for nodes
            min_size = 10
            max_size = 30

            # Add nodes to the network
            for record in nodes:
                node_id = record["id"]
                labels = record["labels"]
                value = record["value"]
                label = f"{labels[0]}: {value}"
                occurrence = record["occurrence"]

                if occurrence is not None and int(occurrence) > 1:
                    label += f"\n(count = {occurrence})"

                # Determine node size based on normalized occurrence
                if occurrence is not None:
                    size = min_size + ((max_size - min_size) * (int(occurrence) / max_occurrence))
                else:
                    size = min_size  # Default size for nodes without occurrence

                if record["details"] is not None:
                    title = record["details"]
                else:
                    title = label

                # Add the node with a calculated size
                net.add_node(
                    node_id,
                    label=label,
                    title=title,
                    group=labels[0],
                    value=size  # Set the size of the node
                )


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

    def load_from_attribute_lists(self, attribute_lists):
        for attribute_list in attribute_lists:
            fixed, var = divide_into_fixed_and_var(attribute_list)
            self.add_user_input(fixed, var)

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
