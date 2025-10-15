"""Unit tests for CognitiveAgent."""

import pytest
from llama_cloud_services.opencog.cognitive_agent import CognitiveAgent
from llama_cloud_services.opencog.atomspace import AtomType


class TestCognitiveAgent:
    """Tests for CognitiveAgent class."""

    def test_agent_creation(self):
        agent = CognitiveAgent(name="test_agent")
        assert agent.name == "test_agent"
        assert agent.atomspace is not None
        assert len(agent.processes) == 3  # Default processes

    def test_add_goal(self):
        agent = CognitiveAgent(name="test_agent")
        goal_id = agent.add_goal("learn Python", priority=0.9)
        assert goal_id is not None

        goals = agent.atomspace.find_atoms(atom_type=AtomType.GOAL)
        assert len(goals) == 1
        assert goals[0].name == "learn Python"

    def test_add_belief(self):
        agent = CognitiveAgent(name="test_agent")
        belief_id = agent.add_belief("Python is useful", strength=0.9)
        assert belief_id is not None

        beliefs = agent.atomspace.find_atoms(atom_type=AtomType.BELIEF)
        assert len(beliefs) == 1

    def test_add_action(self):
        agent = CognitiveAgent(name="test_agent")
        action_id = agent.add_action("study Python tutorial", success_prob=0.8)
        assert action_id is not None

        actions = agent.atomspace.find_atoms(atom_type=AtomType.ACTION)
        assert len(actions) == 1

    def test_perceive(self):
        agent = CognitiveAgent(name="test_agent")
        observations = [
            {"concept": "user request", "strength": 0.9, "confidence": 0.8},
            {"concept": "help needed", "strength": 0.8, "confidence": 0.7},
        ]

        result = agent.perceive(observations)
        assert result["process"] == "perception"
        assert result["count"] == 2

    def test_perceive_string_observations(self):
        agent = CognitiveAgent(name="test_agent")
        observations = ["observation1", "observation2"]

        result = agent.perceive(observations)
        assert result["process"] == "perception"
        assert result["count"] == 2

    def test_reason(self):
        agent = CognitiveAgent(name="test_agent")
        agent.add_goal("help user", priority=0.9)
        agent.add_belief("user needs help", strength=0.9)

        result = agent.reason()
        assert result["process"] == "reasoning"
        assert "beliefs_considered" in result

    def test_plan_actions(self):
        agent = CognitiveAgent(name="test_agent")
        agent.add_goal("complete task", priority=0.9)
        agent.add_action("execute task", success_prob=0.8)

        result = agent.plan_actions()
        assert result["process"] == "action"
        assert "selected_actions" in result

    def test_cognitive_cycle(self):
        agent = CognitiveAgent(name="test_agent")
        agent.add_goal("help user", priority=0.9)
        agent.add_action("provide help", success_prob=0.8)

        observations = [{"concept": "user needs help", "strength": 0.9}]
        result = agent.cognitive_cycle(observations)

        assert result["agent"] == "test_agent"
        assert "cycle_results" in result
        assert "perception" in result["cycle_results"]
        assert "reasoning" in result["cycle_results"]
        assert "action_planning" in result["cycle_results"]

    def test_cognitive_cycle_no_observations(self):
        agent = CognitiveAgent(name="test_agent")
        agent.add_goal("test goal")

        result = agent.cognitive_cycle()
        assert "cycle_results" in result
        assert "perception" not in result["cycle_results"]  # No observations provided
        assert "reasoning" in result["cycle_results"]

    def test_get_knowledge_summary(self):
        agent = CognitiveAgent(name="test_agent")
        agent.add_goal("goal1", priority=0.9)
        agent.add_goal("goal2", priority=0.7)
        agent.add_belief("belief1")
        agent.add_action("action1")

        summary = agent.get_knowledge_summary()
        assert summary["agent"] == "test_agent"
        assert summary["total_atoms"] == 4
        assert summary["goals"] == 2

    def test_export_knowledge(self):
        agent = CognitiveAgent(name="test_agent")
        agent.add_goal("test goal")
        agent.add_belief("test belief")

        exported = agent.export_knowledge()
        assert exported["agent"] == "test_agent"
        assert "atomspace" in exported
        assert len(exported["processes"]) == 3

    def test_agent_with_custom_processes(self):
        from llama_cloud_services.opencog.cognitive_processes import PerceptionProcess

        custom_process = PerceptionProcess(name="custom_perception")
        agent = CognitiveAgent(name="test_agent", processes=[custom_process])

        assert len(agent.processes) == 1
        assert agent.processes[0].name == "custom_perception"
