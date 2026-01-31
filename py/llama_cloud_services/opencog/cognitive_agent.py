"""
CognitiveAgent: Autonomous agent with OpenCog-inspired cognitive architecture.

This agent integrates perception, reasoning, and action processes with
LlamaCloud services for autonomous operation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from llama_cloud_services.opencog.atomspace import AtomSpace
from llama_cloud_services.opencog.cognitive_processes import (
    PerceptionProcess,
    ReasoningProcess,
    ActionProcess,
    CognitiveProcess,
)
from llama_cloud_services.beta.agent_data.client import AsyncAgentDataClient


class CognitiveAgent(BaseModel):
    """
    Autonomous agent with cognitive architecture.
    
    Integrates OpenCog-inspired cognitive processes with LlamaCloud
    services to enable autonomous goal-directed behavior.
    
    Example:
        ```python
        from llama_cloud_services.opencog import CognitiveAgent
        
        # Create agent
        agent = CognitiveAgent(name="assistant")
        
        # Set goals
        agent.add_goal("help user", priority=0.9)
        agent.add_goal("learn new information", priority=0.7)
        
        # Process observations
        result = agent.perceive([
            {"concept": "user needs help with Python", "strength": 0.9},
            {"concept": "documentation available", "strength": 0.8},
        ])
        
        # Run cognitive cycle
        cycle_result = agent.cognitive_cycle()
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(description="Name of the cognitive agent")
    atomspace: AtomSpace = Field(default_factory=lambda: AtomSpace(name="agent_memory"))
    processes: List[CognitiveProcess] = Field(default_factory=list)
    deployment_name: Optional[str] = Field(
        default=None, description="LlamaCloud deployment name for data persistence"
    )
    collection: str = Field(
        default="cognitive_agent", description="Collection name for agent data"
    )
    _agent_data_client: Optional[AsyncAgentDataClient] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize default cognitive processes
        if not self.processes:
            self.processes = [
                PerceptionProcess(),
                ReasoningProcess(),
                ActionProcess(),
            ]

    def add_goal(self, goal: str, priority: float = 0.5) -> str:
        """Add a goal for the agent to pursue."""
        atom = self.atomspace.add_goal(goal, priority=priority)
        return atom.id

    def add_belief(self, belief: str, strength: float = 0.8, confidence: float = 0.7) -> str:
        """Add a belief to the agent's knowledge base."""
        atom = self.atomspace.add_belief(belief, strength=strength, confidence=confidence)
        return atom.id

    def add_action(self, action: str, success_prob: float = 0.5) -> str:
        """Register an action the agent can take."""
        atom = self.atomspace.add_action(action, success_prob=success_prob)
        return atom.id

    def perceive(self, observations: List[Any]) -> Dict[str, Any]:
        """
        Process sensory observations and update knowledge base.
        
        Args:
            observations: List of observations (dict or string)
            
        Returns:
            Dictionary with perception results
        """
        perception_process = next(
            (p for p in self.processes if isinstance(p, PerceptionProcess)), None
        )
        if not perception_process:
            return {"error": "No perception process available"}

        context = {"observations": observations}
        return perception_process.process(self.atomspace, context)

    def reason(self) -> Dict[str, Any]:
        """
        Perform reasoning over current knowledge base.
        
        Returns:
            Dictionary with reasoning results
        """
        reasoning_process = next(
            (p for p in self.processes if isinstance(p, ReasoningProcess)), None
        )
        if not reasoning_process:
            return {"error": "No reasoning process available"}

        return reasoning_process.process(self.atomspace, {})

    def plan_actions(self) -> Dict[str, Any]:
        """
        Select actions to achieve goals.
        
        Returns:
            Dictionary with selected actions
        """
        action_process = next(
            (p for p in self.processes if isinstance(p, ActionProcess)), None
        )
        if not action_process:
            return {"error": "No action process available"}

        return action_process.process(self.atomspace, {})

    def cognitive_cycle(
        self, observations: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete cognitive cycle: perceive -> reason -> act.
        
        Args:
            observations: Optional new observations to perceive
            
        Returns:
            Dictionary with results from each process
        """
        results = {
            "agent": self.name,
            "cycle_results": {},
        }

        # Perceive
        if observations:
            results["cycle_results"]["perception"] = self.perceive(observations)

        # Reason
        results["cycle_results"]["reasoning"] = self.reason()

        # Plan actions
        results["cycle_results"]["action_planning"] = self.plan_actions()

        return results

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's current knowledge."""
        return {
            "agent": self.name,
            "total_atoms": len(self.atomspace.atoms),
            "beliefs": len(
                self.atomspace.find_atoms(atom_type=self.atomspace.atoms[list(self.atomspace.atoms.keys())[0]].type.__class__.BELIEF)
                if self.atomspace.atoms
                else []
            ),
            "goals": len(
                [a for a in self.atomspace.atoms.values() 
                 if hasattr(a.type, 'value') and a.type.value == "goal"]
            ),
            "actions": len(
                [a for a in self.atomspace.atoms.values()
                 if hasattr(a.type, 'value') and a.type.value == "action"]
            ),
            "implications": len(
                [a for a in self.atomspace.atoms.values()
                 if hasattr(a.type, 'value') and a.type.value == "implication"]
            ),
        }

    def export_knowledge(self) -> Dict[str, Any]:
        """Export the agent's knowledge base."""
        return {
            "agent": self.name,
            "atomspace": self.atomspace.to_dict(),
            "processes": [p.name for p in self.processes],
        }

    async def sync_to_cloud(self, client: AsyncAgentDataClient) -> None:
        """
        Sync agent state to LlamaCloud for persistence.
        
        Args:
            client: AsyncAgentDataClient for cloud storage
        """
        knowledge = self.export_knowledge()
        await client.create_agent_data(knowledge)

    async def load_from_cloud(
        self, client: AsyncAgentDataClient, agent_id: str
    ) -> None:
        """
        Load agent state from LlamaCloud.
        
        Args:
            client: AsyncAgentDataClient for cloud storage
            agent_id: ID of the agent data to load
        """
        data = await client.get_agent_data(agent_id)
        if data:
            # Reconstruct atomspace from saved data
            # This is a simplified version - full implementation would
            # properly deserialize all atoms and relationships
            pass
