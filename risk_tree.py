from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from risk_assessment import RiskAssessment

class RiskTree:
    def __init__(self, data):
        self.root_nodes = []
        for root_key in data:
            root_node = Node(root_key)
            self.create_tree(data[root_key], root_node)
            self.root_nodes.append(root_node)

    @staticmethod
    def convertRiskAssessmentsToTree(riskAssessments):
        data = {}
        for riskAssessment in riskAssessments:
            try:
                for key, value in riskAssessment.items():
                    if key == 'risk_level':
                        continue
                    if key not in data:
                        data[key] = {}
                    if value not in data[key]:
                        data[key][value] = []
                    data[key][value].append(riskAssessment['risk_level'])
            except:
                pass
        
        return data

    def average(self, lst):
        return sum(lst) / len(lst) if lst else 0

    def create_tree(self, data, parent=None):
        for key, value in data.items():
            if isinstance(value, dict):
                node = Node(key, parent=parent)
                self.create_tree(value, node)
            else:
                Node(f"{key}: {self.average(value):.2f}", parent=parent)

    def render(self):
        for root in self.root_nodes:
            for pre, fill, node in RenderTree(root):
                print("%s%s" % (pre, node.name))

    def export(self):
        for root in self.root_nodes:
            DotExporter(root).to_picture(f"{root.name}.png")

# # Create several RiskAssessment objects with various categories and risk levels
# risk_assessments = [
#     RiskAssessment(risk_level="low", category1="object", category2="physical", category3="fictional"),
#     RiskAssessment(risk_level="medium", category1="object", category2="physical", category3="real"),
#     RiskAssessment(risk_level="high", category1="person", category2="physical", category3="real"),
#     RiskAssessment(risk_level="low", category1="person", category2="digital", category3="fictional"),
#     RiskAssessment(risk_level="medium", category1="object", category2="digital", category3="fictional"),
# ]

# # Convert the RiskAssessment objects to a tree structure
# data = RiskTree.convertRiskAssessmentsToTree(risk_assessments)

# # Initialize the RiskTree with the converted data
# risk_tree = RiskTree(data)

# # Render the tree to the console
# risk_tree.render()

# # Export the tree to PNG files
# risk_tree.export()