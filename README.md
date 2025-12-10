# Minimal Agent Workflow Engine (AI Engineering Assignment)

This project is a small backend-only workflow / graph engine built with **FastAPI**.

It is a simplified version of systems like LangGraph: you define nodes, edges, shared state, and the engine executes the workflow step-by-step, supporting branching and looping. It also includes a sample **Code Review Mini-Agent** workflow as required.

---

## Features

- **Nodes**  
  - Each node is a Python "tool" function.  
  - Signature: `tool(state: dict, config: dict) -> dict`.  
  - Tools read and update a shared `state` dictionary.

- **Shared State**  
  - A single `dict` flows through the graph.  
  - Each node can read/write keys on the state.

- **Edges & Control Flow**  
  - Simple linear edges: `"current": "next"`.  
  - Conditional / branching edges:
    ```json
    {
      "type": "conditional",
      "condition_key": "quality_score",
      "operator": "lt",
      "value": 0.8,
      "true_next": "suggest_improvements",
      "false_next": "__end__"
    }
    ```
  - Branching + looping are expressed by pointing edges back to previous nodes.
  - Safety: configurable `max_steps` per graph to avoid infinite loops.

- **Tool Registry**  
  - Simple registry mapping a `tool_name` (string) to a Python function.
  - Tools are registered at import time (see `app/workflows/code_review.py`).

- **FastAPI Endpoints**
  - `POST /graph/create` – register a new graph definition.
  - `POST /graph/run` – run a graph with an initial state.
  - `GET /graph/state/{run_id}` – fetch the final state and execution log.
  - `GET /health` – basic health check.

- **In-memory Storage**
  - Graphs and runs are kept in memory using simple dictionaries.
  - Easy to swap out with a database (e.g., SQLite/Postgres) in the future.

---

## Project Structure

```text
app/
  main.py              # FastAPI app and routes
  engine/
    models.py          # NodeDefinition, ExecutionLogEntry
    engine.py          # run_graph_execution, branching, looping
    registry.py        # ToolRegistry and global tool_registry
  storage/
    memory.py          # In-memory stores for graphs and runs
  workflows/
    code_review.py     # Code Review Mini-Agent tools (registered on import)
README.md
requirements.txt
