from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.engine.engine import run_graph_execution
from app.workflows import code_review
from datetime import datetime

from app.storage.memory import GRAPHS, RUNS, generate_id

app = FastAPI(title="Minimal Agent Workflow Engine")



class GraphCreateRequest(BaseModel):
    nodes: Dict[str, Dict[str, Any]]
    edges: Dict[str, Any]
    start_node: str
    max_steps: int | None = 50


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    graph_id: str
    state: Dict[str, Any]


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[Dict[str, Any]]


class RunStateResponse(BaseModel):
    run_id: str
    state: Dict[str, Any]
    log: List[Dict[str, Any]]


@app.get("/health")
def health_check():
    return {"status": "ok"}



@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph(payload: GraphCreateRequest):
    graph_id = generate_id()
        
    GRAPHS[graph_id] = {
        "nodes": payload.nodes,
        "edges": payload.edges,
        "start_node": payload.start_node,
        "max_steps": payload.max_steps or 50,
    }
    return GraphCreateResponse(graph_id=graph_id)


@app.post("/graph/run", response_model=GraphRunResponse)
def run_graph(payload: GraphRunRequest):
    graph = GRAPHS.get(payload.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    run_id = generate_id()

    final_state, exec_log = run_graph_execution(graph, payload.state)

    
    RUNS[run_id] = {
        "graph_id": payload.graph_id,
        "state": final_state,
        "log": [entry.model_dump() for entry in exec_log],
        "started_at": datetime.utcnow().isoformat(),
    }

    return GraphRunResponse(
        run_id=run_id,
        final_state=final_state,
        log=[entry.model_dump() for entry in exec_log],
    )


@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
def get_run_state(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return RunStateResponse(
        run_id=run_id,
        state=run["state"],
        log=run["log"],
    )
