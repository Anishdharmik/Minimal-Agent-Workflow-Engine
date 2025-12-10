from typing import Dict, Any
from uuid import uuid4
from datetime import datetime


GRAPHS: Dict[str, Dict[str, Any]] = {}


RUNS: Dict[str, Dict[str, Any]] = {}


def generate_id() -> str:
    return uuid4().hex
