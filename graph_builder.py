import json
from typing import Dict, Tuple, List
from models import GraphExtraction, Node, Edge

class GraphBuilder:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[Tuple[str, str, str], Edge] = {}

    def add_extraction(self, extraction: GraphExtraction):
        for node in extraction.nodes:
            if node.id in self.nodes:
                for chunk in node.source_chunks:
                    if chunk not in self.nodes[node.id].source_chunks:
                        self.nodes[node.id].source_chunks.append(chunk)
                self.nodes[node.id].attributes.update(node.attributes)
            else:
                self.nodes[node.id] = node

        
        for edge in extraction.edges:
            edge_key = (edge.source_id, edge.target_id, edge.relation)
            if edge_key in self.edges:
                for chunk in edge.source_chunks:
                    if chunk not in self.edges[edge_key].source_chunks:
                        self.edges[edge_key].source_chunks.append(chunk)
            else:
                self.edges[edge_key] = edge

    def build_graph(self) -> str:
        graph_dict = {
            "nodes": [node.model_dump() for node in self.nodes.values()],
            "edges": [edge.model_dump() for edge in self.edges.values()]
        }
        return json.dumps(graph_dict, indent=2)

    def render_mermaid(self) -> str:
        lines = ["graph TD"]
        for node in self.nodes.values():
            label_text = f"{node.type}: {node.label}"
            if node.attributes:
                attr_str = "; ".join([f"{k}={v}" for k, v in node.attributes.items()])
                label_text += f"<br/><b>Attributes</b>: {attr_str}"
            label_text = label_text.replace('"', "'")
            lines.append(f'    {node.id}["{label_text}"]')

        for edge in self.edges.values():
            lines.append(f'    {edge.source_id} -->|{edge.relation}| {edge.target_id}')
        return "\n".join(lines)

    def retrive_chunks(self, query: str) -> List[str]:
        query = query.lower()
        relevant_chunks = set()

        for node in self.nodes.values():
            if query in node.id or query in node.label.lower():
                relevant_chunks.update(node.source_chunks)
                
        for edge in self.edges.values():
            if query in edge.relation.lower():
                relevant_chunks.update(edge.source_chunks)
                
        return list(relevant_chunks)