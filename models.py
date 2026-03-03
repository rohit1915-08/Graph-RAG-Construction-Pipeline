from typing import List, Dict, Any
from pydantic import BaseModel, Field

class Node(BaseModel):
    id: str
    label: str
    type: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    source_chunks: List[str] = Field(default_factory=list)

class Edge(BaseModel):
    source_id: str
    target_id: str
    relation: str
    source_chunks: List[str] = Field(default_factory=list)

class GraphExtraction(BaseModel):
    nodes: List[Node]
    edges: List[Edge]