from typing import Dict, Any, List
import re

from app.engine.registry import tool_registry


State = Dict[str, Any]


def extract_functions_tool(state: State, config: State) -> State:
    
    code: str = state.get("code", "")
    function_names: List[str] = []

    for line in code.splitlines():
        line = line.strip()
        if line.startswith("def "):
            # match def func_name(
            match = re.match(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
            if match:
                function_names.append(match.group(1))

    state["functions"] = function_names
    state["function_count"] = len(function_names)
    return state


def check_complexity_tool(state: State, config: State) -> State:
    
    code: str = state.get("code", "")
    lines = [ln for ln in code.splitlines() if ln.strip()]
    complexity_score = len(lines)

    state["complexity_score"] = complexity_score
    return state


def detect_issues_tool(state: State, config: State) -> State:
    
    issues: List[str] = []

    if state.get("function_count", 0) == 0:
        issues.append("No functions defined; consider modularizing the code.")

    if state.get("complexity_score", 0) > 50:
        issues.append("File is long; consider splitting into smaller modules.")

    code: str = state.get("code", "")
    long_lines = [ln for ln in code.splitlines() if len(ln) > 80]
    if long_lines:
        issues.append("Some lines exceed 80 characters; consider reformatting.")

    state["issues"] = issues
    state["issue_count"] = len(issues)
    return state


def suggest_improvements_tool(state: State, config: State) -> State:
    
    issues: List[str] = state.get("issues", [])
    suggestions: List[str] = []

    for issue in issues:
        if "No functions" in issue:
            suggestions.append("Refactor repeated logic into functions.")
        elif "long; consider splitting" in issue:
            suggestions.append("Split the file into smaller modules by feature.")
        elif "80 characters" in issue:
            suggestions.append("Wrap long lines to keep them readable.")
        else:
            suggestions.append(f"Address issue: {issue}")

    
    iterations = state.get("review_iterations", 0) + 1
    state["review_iterations"] = iterations

    
    issue_count = state.get("issue_count", 0)
    if issue_count > 0:
        issue_count -= 1
    state["issue_count"] = issue_count

    state["suggestions"] = suggestions
    return state


def evaluate_quality_tool(state: State, config: State) -> State:
    
    base = 0.4
    iterations = state.get("review_iterations", 0)
    remaining_issues = state.get("issue_count", 0)

    
    quality_score = base + 0.15 * iterations - 0.1 * remaining_issues
    
    quality_score = max(0.0, min(1.0, quality_score))

    state["quality_score"] = quality_score
    return state




tool_registry.register("extract_functions", extract_functions_tool)
tool_registry.register("check_complexity", check_complexity_tool)
tool_registry.register("detect_issues", detect_issues_tool)
tool_registry.register("suggest_improvements", suggest_improvements_tool)
tool_registry.register("evaluate_quality", evaluate_quality_tool)
