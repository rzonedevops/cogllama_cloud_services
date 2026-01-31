"""
Example: Using OpenCog-inspired Cognitive Agent with LlamaCloud Services

This example demonstrates how to use the CognitiveAgent to create an
autonomous agent with goals, beliefs, and reasoning capabilities.
"""

from llama_cloud_services import CognitiveAgent


def basic_cognitive_agent_example():
    """Basic example of creating and using a cognitive agent."""
    print("=" * 60)
    print("Basic Cognitive Agent Example")
    print("=" * 60)

    # Create a cognitive agent
    agent = CognitiveAgent(name="assistant_agent")

    # Define goals for the agent
    print("\n1. Setting agent goals...")
    agent.add_goal("help user with Python", priority=0.9)
    agent.add_goal("learn new information", priority=0.7)
    agent.add_goal("improve responses", priority=0.6)

    # Add available actions
    print("2. Registering available actions...")
    agent.add_action("search documentation", success_prob=0.8)
    agent.add_action("provide code example", success_prob=0.7)
    agent.add_action("ask clarifying question", success_prob=0.9)

    # Process observations
    print("3. Processing observations...")
    observations = [
        {"concept": "user needs help with Python functions", "strength": 0.9, "confidence": 0.9},
        {"concept": "user is a beginner", "strength": 0.7, "confidence": 0.8},
        {"concept": "documentation is available", "strength": 0.8, "confidence": 0.9},
    ]
    perception_result = agent.perceive(observations)
    print(f"   Perceived {perception_result['count']} concepts")

    # Run reasoning process
    print("4. Running reasoning process...")
    reasoning_result = agent.reason()
    print(f"   Considered {reasoning_result['beliefs_considered']} beliefs")
    print(f"   Evaluated {reasoning_result['goals_considered']} goals")

    # Plan actions
    print("5. Planning actions...")
    action_result = agent.plan_actions()
    print(f"   Selected {len(action_result['selected_actions'])} actions")
    for action in action_result["selected_actions"]:
        print(f"   - {action['action']} (score: {action['score']:.2f})")

    # Get knowledge summary
    print("\n6. Agent knowledge summary:")
    summary = agent.get_knowledge_summary()
    print(f"   Total atoms: {summary['total_atoms']}")
    print(f"   Goals: {summary['goals']}")
    print(f"   Actions: {summary['actions']}")
    print(f"   Implications: {summary['implications']}")


def cognitive_cycle_example():
    """Example of running a complete cognitive cycle."""
    print("\n" + "=" * 60)
    print("Cognitive Cycle Example")
    print("=" * 60)

    agent = CognitiveAgent(name="learning_agent")

    # Setup
    agent.add_goal("understand user intent", priority=0.9)
    agent.add_goal("provide helpful response", priority=0.8)
    agent.add_action("analyze input", success_prob=0.85)
    agent.add_action("generate response", success_prob=0.75)

    # Run cognitive cycle with new observations
    observations = [
        {"concept": "user asking about lists", "strength": 0.9},
        {"concept": "user confused about syntax", "strength": 0.7},
    ]

    print("\nRunning cognitive cycle...")
    result = agent.cognitive_cycle(observations)

    print(f"\nAgent: {result['agent']}")
    print("\nCycle results:")
    for process_name, process_result in result["cycle_results"].items():
        print(f"  {process_name}:")
        if isinstance(process_result, dict):
            for key, value in process_result.items():
                if key != "process":
                    print(f"    - {key}: {value}")


def knowledge_graph_example():
    """Example of working with the AtomSpace knowledge graph."""
    print("\n" + "=" * 60)
    print("Knowledge Graph Example")
    print("=" * 60)

    agent = CognitiveAgent(name="knowledge_agent")

    # Build knowledge graph
    print("\n1. Building knowledge graph...")
    
    # Add concepts using AtomType
    from llama_cloud_services.opencog.atomspace import AtomType
    
    concept1 = agent.atomspace.add_atom(
        atom_type=AtomType.CONCEPT,
        name="Python programming"
    )
    
    # Add beliefs
    belief1 = agent.add_belief("Python is beginner-friendly", strength=0.9)
    belief2 = agent.add_belief("Python has great libraries", strength=0.95)
    
    # Add goals
    goal1 = agent.add_goal("teach Python effectively", priority=0.9)
    
    print(f"   Added beliefs, goals, and concepts")

    # Query knowledge graph
    print("\n2. Querying knowledge graph...")
    
    beliefs = agent.atomspace.find_atoms(atom_type=AtomType.BELIEF)
    print(f"   Found {len(beliefs)} beliefs:")
    for belief in beliefs:
        print(f"   - {belief.name} (strength: {belief.truth_value.strength:.2f})")

    goals = agent.atomspace.find_atoms(atom_type=AtomType.GOAL)
    print(f"\n   Found {len(goals)} goals:")
    for goal in goals:
        print(f"   - {goal.name} (priority: {goal.truth_value.strength:.2f})")


def autonomous_agent_scenario():
    """Example of an autonomous agent scenario."""
    print("\n" + "=" * 60)
    print("Autonomous Agent Scenario")
    print("=" * 60)

    # Create an agent with specific purpose
    agent = CognitiveAgent(name="tutorial_assistant")

    # Define agent's goals
    agent.add_goal("help user learn Python", priority=0.95)
    agent.add_goal("provide clear examples", priority=0.85)
    agent.add_goal("maintain user engagement", priority=0.75)

    # Define agent's capabilities
    agent.add_action("provide code example", success_prob=0.9)
    agent.add_action("explain concept", success_prob=0.85)
    agent.add_action("suggest practice exercise", success_prob=0.8)
    agent.add_action("recommend resources", success_prob=0.75)

    # Initial beliefs
    agent.add_belief("users learn best by doing", strength=0.9)
    agent.add_belief("examples clarify concepts", strength=0.85)

    print("\nAgent initialized with goals, actions, and beliefs")

    # Simulate interaction over multiple cycles
    scenarios = [
        {
            "name": "User asks about functions",
            "observations": [
                {"concept": "user interested in functions", "strength": 0.9},
                {"concept": "user needs examples", "strength": 0.8},
            ],
        },
        {
            "name": "User practices code",
            "observations": [
                {"concept": "user writing code", "strength": 0.85},
                {"concept": "user making progress", "strength": 0.7},
            ],
        },
        {
            "name": "User needs clarification",
            "observations": [
                {"concept": "user confused", "strength": 0.8},
                {"concept": "concept needs explanation", "strength": 0.9},
            ],
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Cycle {i}: {scenario['name']} ---")
        result = agent.cognitive_cycle(scenario["observations"])

        # Show selected actions
        actions = result["cycle_results"]["action_planning"]["selected_actions"]
        if actions:
            print(f"Agent selects: {actions[0]['action']}")
            print(f"  For goal: {actions[0]['goal']}")
            print(f"  Confidence: {actions[0]['score']:.2f}")
        else:
            print("Agent: No action needed at this time")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("OpenCog Cognitive Agent Examples")
    print("LlamaCloud Services Integration")
    print("=" * 60)

    try:
        basic_cognitive_agent_example()
        cognitive_cycle_example()
        knowledge_graph_example()
        autonomous_agent_scenario()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
