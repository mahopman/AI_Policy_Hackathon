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
        data = {"victim": {}, "type": {}, "reality": {}}
        for riskAssessment in riskAssessments:
            if riskAssessment.victim not in data["victim"]:
                data["victim"][riskAssessment.victim] = []
            data["victim"][riskAssessment.victim].append(riskAssessment.risk)
            if riskAssessment.type not in data["type"]:
                data["type"][riskAssessment.type] = []
            data["type"][riskAssessment.type].append(riskAssessment.risk)
            if riskAssessment.reality not in data["reality"]:
                data["reality"][riskAssessment.reality] = []
            data["reality"][riskAssessment.reality].append(riskAssessment.risk)
        
        return data

    def average(self, lst):
        return sum(lst) / len(lst) if lst else 0

    def create_tree(self, data, parent=None):
        for key, value in data.items():
            if isinstance(value, dict):
                node = Node(key, parent=parent)
                self.create_tree(value, node)
            else:
                avg_value = self.average(value)
                Node(f"{key} (avg: {avg_value})", parent=parent)

    def render(self):
        for root in self.root_nodes:
            for pre, fill, node in RenderTree(root):
                print("%s%s" % (pre, node.name))

    def export(self):
        for root in self.root_nodes:
            DotExporter(root).to_picture(f"{root.name}.png")

# Uncomment to test:
# data = RiskTree.convertRiskAssessmentsToTree([RiskAssessment("object", "physical", "fictional", 0.5), RiskAssessment("person", "physical", "real", 0.3)])
# print(data)
# riskTree = RiskTree(data)
# riskTree.render()