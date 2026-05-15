from fastapi import Request, Depends
from typing import Annotated
from langgraph.graph.state import CompiledStateGraph


def get_db_client(request: Request) -> CompiledStateGraph:
    """получение agent из app.state."""
    return request.app.state.agent

Agent = Annotated[CompiledStateGraph, Depends(get_db_client)]
