from typing import Dict, Any, List, Tuple, Union
from app.engine.models import ExecutionLogEntry, NodeDefinition
from app.engine.registry import tool_registry


EdgeDef = Union[str, Dict[str, Any]]  


def _evaluate_condition(
    state: Dict[str, Any],
    condition_key: str,
    operator: str,
    value: Any,
) -> bool:
    
    left = state.get(condition_key)

    if operator == "lt":
        return left < value
    if operator == "lte":
        return left <= value
    if operator == "gt":
        return left > value
    if operator == "gte":
        return left >= value
    if operator == "eq":
        return left == value
    if operator == "ne":
        return left != value

    
    return False


def _resolve_next_node(edge_def: EdgeDef, state: Dict[str, Any]) -> str | None:
    
    
    if isinstance(edge_def, str):
        if edge_def == "__end__":
            return None
        return edge_def

    
    if isinstance(edge_def, dict):
        edge_type = edge_def.get("type")

        if edge_type == "conditional":
            condition_key = edge_def["condition_key"]
            operator = edge_def["operator"]
            value = edge_def["value"]
            true_next = edge_def.get("true_next")
            false_next = edge_def.get("false_next")

            outcome = _evaluate_condition(state, condition_key, operator, value)
            chosen = true_next if outcome else false_next

            if chosen == "__end__":
                return None
            return chosen

    
    return None


def run_graph_execution(
    graph: Dict[str, Any],
    initial_state: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[ExecutionLogEntry]]:
    
    nodes_raw: Dict[str, Dict[str, Any]] = graph["nodes"]
    edges: Dict[str, EdgeDef] = graph.get("edges", {})
    start_node: str = graph["start_node"]
    max_steps: int = graph.get("max_steps", 50)

   
    node_defs: Dict[str, NodeDefinition] = {}

    for node_name, node_data in nodes_raw.items():
        node_defs[node_name] = NodeDefinition(
            name=node_name,
            tool_name=node_data["tool_name"],
            config=node_data.get("config", {}),
        )

    state = dict(initial_state)
    log: List[ExecutionLogEntry] = []

    current_node_name: str | None = start_node
    steps = 0

    while current_node_name is not None and steps < max_steps:
        node_def = node_defs.get(current_node_name)
        if node_def is None:
            
            log.append(
                ExecutionLogEntry(
                    node=current_node_name,
                    state_snapshot=state.copy(),
                    message=f"Node '{current_node_name}' not found. Stopping execution.",
                )
            )
            break

        try:
            tool = tool_registry.get(node_def.tool_name)
        except KeyError as e:
            log.append(
                ExecutionLogEntry(
                    node=current_node_name,
                    state_snapshot=state.copy(),
                    message=str(e),
                )
            )
            break

        
        try:
            new_state = tool(state, node_def.config)
            if new_state is None:
                
                new_state = state
            state = new_state
            log.append(
                ExecutionLogEntry(
                    node=current_node_name,
                    state_snapshot=state.copy(),
                    message=f"Executed tool '{node_def.tool_name}'",
                )
            )
        except Exception as exc:
            log.append(
                ExecutionLogEntry(
                    node=current_node_name,
                    state_snapshot=state.copy(),
                    message=f"Error during execution: {exc}",
                )
            )
            break

        
        edge_def = edges.get(current_node_name)
        current_node_name = _resolve_next_node(edge_def, state)
        steps += 1

    if steps >= max_steps:
        log.append(
            ExecutionLogEntry(
                node=current_node_name or "unknown",
                state_snapshot=state.copy(),
                message=f"Max steps {max_steps} reached, stopping to avoid infinite loop.",
            )
        )

    return state, log
