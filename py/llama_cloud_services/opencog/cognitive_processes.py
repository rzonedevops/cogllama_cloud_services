"""
Cognitive processes for autonomous agents.

Inspired by OpenCog's cognitive architecture, this module implements
perception, reasoning, and action processes.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from llama_cloud_services.opencog.atomspace import AtomSpace, Atom, AtomType, TruthValue


class CognitiveProcess(BaseModel):
    """Base class for cognitive processes."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    enabled: bool = True

    def process(self, atomspace: AtomSpace, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the cognitive process."""
        raise NotImplementedError("Subclasses must implement process()")


class PerceptionProcess(CognitiveProcess):
    """
    Perception process: Transform sensory input into knowledge.
    
    This process takes external observations and adds them to the
    agent's knowledge base (AtomSpace) as beliefs.
    """

    name: str = "perception"

    def process(self, atomspace: AtomSpace, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process perceptual input and update knowledge base."""
        observations = context.get("observations", [])
        perceived_concepts = []

        for observation in observations:
            if isinstance(observation, dict):
                concept_name = observation.get("concept", "unknown")
                strength = observation.get("strength", 0.7)
                confidence = observation.get("confidence", 0.8)
            else:
                concept_name = str(observation)
                strength = 0.7
                confidence = 0.8

            # Add perception as belief
            atom = atomspace.add_belief(
                belief=f"perceived:{concept_name}",
                strength=strength,
                confidence=confidence,
            )
            perceived_concepts.append(atom.id)

        return {
            "process": self.name,
            "perceived_concepts": perceived_concepts,
            "count": len(perceived_concepts),
        }


class ReasoningProcess(CognitiveProcess):
    """
    Reasoning process: Infer new knowledge from existing knowledge.
    
    This process performs logical inference, pattern matching, and
    knowledge integration to derive new beliefs and implications.
    """

    name: str = "reasoning"
    inference_threshold: float = Field(
        default=0.6, description="Minimum confidence for inference"
    )

    def process(self, atomspace: AtomSpace, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform reasoning over the knowledge base."""
        inferences = []

        # Find high-confidence beliefs
        beliefs = atomspace.find_atoms(
            atom_type=AtomType.BELIEF, min_strength=self.inference_threshold
        )

        # Find active goals
        goals = atomspace.find_atoms(atom_type=AtomType.GOAL)

        # Simple goal-belief matching reasoning
        for goal in goals:
            if goal.metadata.get("status") != "active":
                continue

            for belief in beliefs:
                # Check if belief is relevant to goal (simple keyword matching)
                if self._is_relevant(goal.name, belief.name):
                    # Create implication: belief -> goal achievable
                    implication = atomspace.add_atom(
                        atom_type=AtomType.IMPLICATION,
                        name=f"{belief.name} => {goal.name}",
                        truth_value=TruthValue(
                            strength=min(belief.truth_value.strength, 0.8),
                            confidence=belief.truth_value.confidence * 0.8,
                        ),
                        outgoing=[belief.id, goal.id],
                    )
                    inferences.append(implication.id)

        return {
            "process": self.name,
            "inferences": inferences,
            "beliefs_considered": len(beliefs),
            "goals_considered": len(goals),
        }

    def _is_relevant(self, goal_name: str, belief_name: str) -> bool:
        """Check if a belief is relevant to a goal."""
        # Simple keyword-based relevance
        goal_words = set(goal_name.lower().split())
        belief_words = set(belief_name.lower().split())
        return len(goal_words & belief_words) > 0


class ActionProcess(CognitiveProcess):
    """
    Action process: Select and execute actions to achieve goals.
    
    This process evaluates potential actions based on goals, beliefs,
    and expected outcomes, then selects the most promising action.
    """

    name: str = "action"
    action_threshold: float = Field(
        default=0.5, description="Minimum probability for action selection"
    )

    def process(self, atomspace: AtomSpace, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select and prepare actions based on goals."""
        selected_actions = []

        # Find active goals sorted by priority
        goals = atomspace.find_atoms(atom_type=AtomType.GOAL)
        active_goals = [
            g for g in goals if g.metadata.get("status") == "active"
        ]
        active_goals.sort(
            key=lambda g: g.truth_value.strength, reverse=True
        )

        # Find available actions
        actions = atomspace.find_atoms(atom_type=AtomType.ACTION)

        # For each goal, find relevant actions
        for goal in active_goals[:3]:  # Consider top 3 goals
            best_action = None
            best_score = 0.0

            for action in actions:
                # Check if action is relevant to goal
                if self._action_helps_goal(action, goal, atomspace):
                    score = self._calculate_action_score(action, goal)
                    if score > best_score and score >= self.action_threshold:
                        best_score = score
                        best_action = action

            if best_action:
                # Create execution plan
                execution = atomspace.add_atom(
                    atom_type=AtomType.EXECUTION,
                    name=f"execute:{best_action.name}",
                    truth_value=TruthValue(strength=best_score, confidence=0.8),
                    outgoing=[best_action.id, goal.id],
                    metadata={
                        "goal_id": goal.id,
                        "action_id": best_action.id,
                        "expected_utility": best_score,
                    },
                )
                selected_actions.append(
                    {
                        "execution_id": execution.id,
                        "action": best_action.name,
                        "goal": goal.name,
                        "score": best_score,
                    }
                )

        return {
            "process": self.name,
            "selected_actions": selected_actions,
            "goals_addressed": len(selected_actions),
        }

    def _action_helps_goal(
        self, action: Atom, goal: Atom, atomspace: AtomSpace
    ) -> bool:
        """Check if an action can help achieve a goal."""
        # Check for implications linking action to goal
        implications = atomspace.find_atoms(atom_type=AtomType.IMPLICATION)
        for imp in implications:
            if action.id in imp.outgoing and goal.id in imp.outgoing:
                return True

        # Fallback: simple name matching
        return self._is_relevant(goal.name, action.name)

    def _calculate_action_score(self, action: Atom, goal: Atom) -> float:
        """Calculate utility score for taking an action toward a goal."""
        # Combine action success probability with goal priority
        action_strength = action.truth_value.strength
        goal_priority = goal.truth_value.strength
        return (action_strength + goal_priority) / 2.0

    def _is_relevant(self, goal_name: str, action_name: str) -> bool:
        """Check if an action is relevant to a goal."""
        goal_words = set(goal_name.lower().split())
        action_words = set(action_name.lower().split())
        return len(goal_words & action_words) > 0
