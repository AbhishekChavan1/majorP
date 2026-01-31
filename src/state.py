"""Project state management using TypedDict"""

from typing import Annotated, Optional, List, Dict
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ProjectState(TypedDict):
    """State management for embedded projects"""
    messages: Annotated[list, add_messages]
    platform: str
    requirements: str
    generated_code: str
    validation_result: Optional[Dict]
    documentation: str
    project_name: str
    current_step: str
    context_chunks: Optional[List[str]]
    error_message: str
    search_results: Optional[List[Dict]]
