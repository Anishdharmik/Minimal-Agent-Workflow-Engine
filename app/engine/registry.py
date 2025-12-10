from typing import Callable, Dict, Any

ToolFunc = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolFunc] = {}

    def register(self, name: str, func: ToolFunc):
        self._tools[name] = func

    def get(self, name: str) -> ToolFunc:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not registered")
        return self._tools[name]



tool_registry = ToolRegistry()
