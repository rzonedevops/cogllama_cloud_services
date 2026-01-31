"""Unit tests for cognitive processes."""

import pytest
from llama_cloud_services.opencog.atomspace import AtomSpace, AtomType
from llama_cloud_services.opencog.cognitive_processes import (
    PerceptionProcess,
    ReasoningProcess,
    ActionProcess,
)


class TestPerceptionProcess:
    """Tests for PerceptionProcess."""

    def test_perception_process_creation(self):
        process = PerceptionProcess()
        assert process.name == "perception"
        assert process.enabled is True

    def test_process_observations_dict(self):
        process = PerceptionProcess()
        atomspace = AtomSpace()
        context = {
            "observations": [
                {"concept": "test1", "strength": 0.8, "confidence": 0.9},
                {"concept": "test2", "strength": 0.7, "confidence": 0.8},
            ]
        }

        result = process.process(atomspace, context)
        assert result["process"] == "perception"
        assert result["count"] == 2
        assert len(result["perceived_concepts"]) == 2

        # Check atoms were added
        beliefs = atomspace.find_atoms(atom_type=AtomType.BELIEF)
        assert len(beliefs) == 2

    def test_process_observations_string(self):
        process = PerceptionProcess()
        atomspace = AtomSpace()
        context = {"observations": ["observation1", "observation2"]}

        result = process.process(atomspace, context)
        assert result["count"] == 2

    def test_process_empty_observations(self):
        process = PerceptionProcess()
        atomspace = AtomSpace()
        context = {"observations": []}

        result = process.process(atomspace, context)
        assert result["count"] == 0


class TestReasoningProcess:
    """Tests for ReasoningProcess."""

    def test_reasoning_process_creation(self):
        process = ReasoningProcess()
        assert process.name == "reasoning"
        assert process.inference_threshold == 0.6

    def test_process_with_beliefs_and_goals(self):
        process = ReasoningProcess()
        atomspace = AtomSpace()

        # Add high-confidence beliefs
        atomspace.add_belief("Python is useful", strength=0.9, confidence=0.9)
        atomspace.add_belief("Learning helps Python", strength=0.8, confidence=0.8)

        # Add goals
        atomspace.add_goal("Learn Python", priority=0.9)

        result = process.process(atomspace, {})
        assert result["process"] == "reasoning"
        assert result["beliefs_considered"] >= 2
        assert result["goals_considered"] >= 1

    def test_process_creates_implications(self):
        process = ReasoningProcess()
        atomspace = AtomSpace()

        atomspace.add_belief("user needs help", strength=0.9, confidence=0.9)
        atomspace.add_goal("help user", priority=0.9)

        initial_count = len(atomspace.atoms)
        result = process.process(atomspace, {})

        # Should create implications
        implications = atomspace.find_atoms(atom_type=AtomType.IMPLICATION)
        assert len(implications) > 0

    def test_process_low_confidence_beliefs(self):
        process = ReasoningProcess(inference_threshold=0.8)
        atomspace = AtomSpace()

        # Add low-confidence belief (below threshold)
        atomspace.add_belief("uncertain fact", strength=0.5, confidence=0.5)
        atomspace.add_goal("test goal", priority=0.9)

        result = process.process(atomspace, {})
        # Low confidence beliefs should not be considered
        assert result["beliefs_considered"] == 0


class TestActionProcess:
    """Tests for ActionProcess."""

    def test_action_process_creation(self):
        process = ActionProcess()
        assert process.name == "action"
        assert process.action_threshold == 0.5

    def test_process_selects_actions_for_goals(self):
        process = ActionProcess()
        atomspace = AtomSpace()

        # Add goal
        goal = atomspace.add_goal("complete task", priority=0.9)

        # Add action
        action = atomspace.add_action("execute task", success_prob=0.8)

        result = process.process(atomspace, {})
        assert result["process"] == "action"
        assert "selected_actions" in result

    def test_process_respects_threshold(self):
        process = ActionProcess(action_threshold=0.9)
        atomspace = AtomSpace()

        atomspace.add_goal("difficult goal", priority=0.5)
        atomspace.add_action("low probability action", success_prob=0.3)

        result = process.process(atomspace, {})
        # Low utility action should not be selected
        assert len(result["selected_actions"]) == 0

    def test_process_prioritizes_goals(self):
        process = ActionProcess()
        atomspace = AtomSpace()

        # Add multiple goals with different priorities
        goal1 = atomspace.add_goal("high priority goal", priority=0.9)
        goal2 = atomspace.add_goal("low priority goal", priority=0.3)

        # Add action that matches both
        action = atomspace.add_action("goal action", success_prob=0.8)

        result = process.process(atomspace, {})
        # Should prioritize high priority goal
        if result["selected_actions"]:
            assert "high priority" in result["selected_actions"][0]["goal"].lower()

    def test_process_creates_executions(self):
        process = ActionProcess()
        atomspace = AtomSpace()

        atomspace.add_goal("test goal", priority=0.9)
        atomspace.add_action("test action", success_prob=0.8)

        initial_count = len(atomspace.atoms)
        result = process.process(atomspace, {})

        # Should create execution plans
        executions = atomspace.find_atoms(atom_type=AtomType.EXECUTION)
        if result["selected_actions"]:
            assert len(executions) > 0

    def test_process_with_no_active_goals(self):
        process = ActionProcess()
        atomspace = AtomSpace()

        # Add goal but mark it as completed
        goal = atomspace.add_goal("completed goal", priority=0.9)
        goal.metadata["status"] = "completed"

        atomspace.add_action("test action", success_prob=0.8)

        result = process.process(atomspace, {})
        # Should not select actions for completed goals
        assert len(result["selected_actions"]) == 0
