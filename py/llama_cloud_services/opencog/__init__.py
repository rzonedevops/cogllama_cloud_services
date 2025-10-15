"""
OpenCog-inspired autonomous agentic platform for LlamaCloud Services.

This module provides a cognitive architecture framework that integrates with
LlamaCloud services to enable autonomous agent behaviors with reasoning,
memory, and goal-directed action.
"""

from llama_cloud_services.opencog.atomspace import AtomSpace, Atom, AtomType
from llama_cloud_services.opencog.cognitive_agent import CognitiveAgent
from llama_cloud_services.opencog.cognitive_processes import (
    PerceptionProcess,
    ReasoningProcess,
    ActionProcess,
)

__all__ = [
    "AtomSpace",
    "Atom",
    "AtomType",
    "CognitiveAgent",
    "PerceptionProcess",
    "ReasoningProcess",
    "ActionProcess",
]
