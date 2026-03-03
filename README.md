# Graph RAG Construction Pipeline

## Overview

A modular, reusable pipeline designed to ingest unstructured text chunks and construct a deterministic, scalable Knowledge Graph. The system extracts entities, strict relationships, and events, resolving them into a unified graph structure ready for Graph RAG applications. Outputs include Graph JSON and paste-ready Mermaid syntax.

## Architecture

The pipeline is split into four distinct modules to separate concerns:

- `models.py`: Defines strict Pydantic schemas (`Node`, `Edge`, `GraphExtraction`) to guarantee uniform data structures.
- `extractor.py`: Handles LLM communication via the Groq API (using the OpenAI Python SDK). Enforces schema adherence through standard JSON mode and Pydantic validation. Includes a mock mode for testing without API calls and strict pipeline-level overrides for provenance.
- `graph_builder.py`: Manages the global graph state. Handles entity deduplication, relation merging, and dynamic source chunk provenance tracking.
- `main.py`: The orchestration script that processes the input chunks, builds the graph, and writes the JSON and Markdown artifacts.

## Key Design Decisions

- **Deterministic Extraction:** Utilized `json_object` mode paired with strict Pydantic validation (`model_validate_json`). This ensures compatibility with high-speed models like Groq's `llama-3.3-70b-versatile` while guaranteeing the output structure never breaks the build logic.
- **Data-Agnostic Entity Resolution:** To strictly adhere to the "no hardcoding" constraint, entity resolution is handled dynamically via prompt rules (e.g., stripping spaces, normalizing lowercase, dropping prefixes) rather than using a hardcoded alias map. This ensures the pipeline works on unseen companies.
- **Pipeline-Level Robustness:** LLMs occasionally hallucinate placeholder strings for arrays (e.g., returning `["chunk_1"]` instead of the actual ID). To make the system robust against LLM variation, the pipeline strictly overrides the LLM's `source_chunks` output by injecting the known, verified `chunk_id` at the Python layer during extraction.
- **Provenance Tracking:** Every node and edge maintains a `source_chunks` list. When a new chunk provides a duplicate fact, the builder dynamically appends the new chunk ID rather than duplicating the entity or edge, fulfilling the expandability requirement.
- **Controlled Ontology:** Edge relations are strictly limited to a predefined set of defensible verbs (`operates`, `offers`, `enabled_by`, `acquired`, `has_event`, `described_in`, etc.) to prevent graph drift and over-claiming. Mandatory `Source` nodes visually map chunks to their core entities.

## Setup & Execution

1. Create a `.env` file in the root directory and add your Groq API key:
   `GROQ_API_KEY=your_api_key_here`
2. Install dependencies:
   `pip install pydantic openai python-dotenv`
3. Run the pipeline:
   `python main.py`

## Output Artifacts

- `output_graph.json`: The complete node/edge structure with attributes and chunk provenance.
- `output_mermaid.md`: The visual representation formatted strictly for Mermaid.js (`graph TD`).

## Bonus Implementation

- **Retrieval Module:** A `retrive_chunks` function is included in `graph_builder.py` (spelling identically matches the assignment prompt). It accepts a user query, maps it against the constructed graph, and returns a deduplicated list of chunk IDs detailing where the relevant nodes or edges were originally sourced.
