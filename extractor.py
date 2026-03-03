import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from models import GraphExtraction

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
You are a knowledge graph extraction engine.
Extract entities, attributes, and events from the provided text chunk.
Do NOT hardcode company names, years, or products. Extract exactly what is in the text.

Rules:
1. ID Generation & Resolution (CRITICAL): Create short, stable, lowercase alphanumeric IDs. 
   - Strip spaces and underscores.
   - Remove company prefixes to find the base entity.
   - Resolve generic references to their specific names IF the context is clear in the chunk.
   - You MUST use the exact same ID for the same entity across different chunks.
2. Node Types: Use generic types like Company, Platform, Service, Partner, Capability, Product, Feature, Event, Acquisition Target, and Source.
3. Source Nodes (MANDATORY): You MUST create a node representing the document/chunk itself (type 'Source', id 'source_{chunk_id}', label 'Chunk {chunk_id}'). Connect the primary Company or Platform node to this Source node using the relation 'described_in'.
4. Event Nodes: If a timeline/year is mentioned, create an Event node (e.g., id 'e2014', label 'Launch Initial Product (2014)').
5. Edge Relations: STRICTLY use ONLY these verbs: operates, offers, enabled_by, supported_by, includes, integrated_surface, executed_via, acquired, has_event, launched, described_in, related_to.

You MUST output a valid JSON object exactly matching this structure:
{
  "nodes": [
    {"id": "str", "label": "str", "type": "str", "attributes": {"key": "value"}, "source_chunks": []}
  ],
  "edges": [
    {"source_id": "str", "target_id": "str", "relation": "str", "source_chunks": []}
  ]
}
"""

def extract(chunk_text: str, chunk_id: str, mock_mode: bool = False) -> GraphExtraction:
    if mock_mode:
        return _mock_extraction(chunk_id)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.replace("{chunk_id}", chunk_id)},
            {"role": "user", "content": f"Text: {chunk_text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    
    json_string = response.choices[0].message.content
    extraction = GraphExtraction.model_validate_json(json_string)
    for node in extraction.nodes:
        node.source_chunks = [chunk_id]
    for edge in extraction.edges:
        edge.source_chunks = [chunk_id]
        
    return extraction

def _mock_extraction(chunk_id: str) -> GraphExtraction:
    with open("mock_data.json", "r") as f:
         data = json.load(f)
    return GraphExtraction(**data.get(chunk_id, {"nodes": [], "edges": []}))