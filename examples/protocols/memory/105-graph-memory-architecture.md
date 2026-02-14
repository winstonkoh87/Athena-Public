# Protocol 105: Graph Memory Architecture (LightRAG)

> **Purpose**: Upgrading Athena's "Brain" from naive vector search to graph-based multi-hop reasoning.
> **Engine**: `lightrag-hku` + `ollama` (Mistral/Llama3).
> **Status**: Experimental (v1.0).

---

## 1. The Theory (Why Graph?)

Standard RAG retrieves chunks based on *keyword similarity*.
**Graph RAG** retrieves chunks based on *relationships*.

- **Standard**: "Find files about 'Risk'." -> Returns `Risk_Management.md`.
- **Graph**: "How does 'Risk' impact 'Strategy'?" -> Traces the edge between `Risk` node and `Strategy` node, even if they never appear in the same file.

## 2. The Architecture

- **Wrapper**: `.agent/scripts/lightrag_wrapper.py`
- **Storage**: `.context/memory_bank/lightrag_store/`
- **Models**:
  - LLM: `mistral` (via Ollama)
  - Embed: `nomic-embed-text` (via Ollama)

## 3. Usage Guide

### A. Indexing (The Learning Phase)

*Run this when you add new significant protocols or memories.*

```bash
# Index specific directory
python3 .agent/scripts/lightrag_wrapper.py --index --dir .agent/skills/protocols/

# Index active context
python3 .agent/scripts/lightrag_wrapper.py --index --dir .context/memory_bank/
```

### B. Querying (The Reasoning Phase)

*Use this for complex, multi-hop questions.*

```bash
python3 .agent/scripts/lightrag_wrapper.py --query "Explain the relationship between Law #1 and the Kelly Criterion" --mode hybrid
```

**Modes**:

- `local`: Best for specific details in a single document cluster.
- `global`: Best for "What are the main themes?" questions.
- `hybrid`: Best of both. (Default).

## 4. Maintenance

- **Pruning**: To reset the graph, delete the `.context/memory_bank/lightrag_store/` directory and re-index.
- **Model Swap**: Edit `DEFAULT_LLM_MODEL` in `lightrag_wrapper.py` to switch to `llama3` or `gemma`.

---

> **Tags**: #memory #graph #rag #architecture
