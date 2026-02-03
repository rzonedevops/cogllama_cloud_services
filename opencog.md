# OpenCog Autonomous Agentic Platform

OpenCog integration for LlamaCloud Services provides a cognitive architecture framework for building autonomous, goal-directed agents with reasoning capabilities.

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Quick Start](#quick-start)
- [AtomSpace Knowledge Graph](#atomspace-knowledge-graph)
- [Cognitive Processes](#cognitive-processes)
- [Cognitive Agent](#cognitive-agent)
- [Integration with LlamaCloud](#integration-with-llamacloud)
- [Examples](#examples)

## Overview

This module implements OpenCog-inspired cognitive architecture that enables:

- **Knowledge Representation**: Graph-based knowledge storage with probabilistic truth values
- **Autonomous Reasoning**: Goal-directed inference and planning
- **Perception-Action Loop**: Process observations and select actions
- **Memory Management**: Persistent knowledge storage via AtomSpace
- **Cloud Integration**: Seamless integration with LlamaCloud services

## Core Concepts

### AtomSpace

The AtomSpace is a graph database that stores knowledge as interconnected atoms with probabilistic truth values. Each atom represents a unit of knowledge such as concepts, beliefs, goals, or actions.

### Cognitive Processes

Three main cognitive processes form the agent's cognitive cycle:

1. **Perception**: Transform sensory input into knowledge
2. **Reasoning**: Infer new knowledge from existing knowledge
3. **Action**: Select actions to achieve goals

### Truth Values

Knowledge is represented with probabilistic truth values consisting of:
- **Strength**: Confidence in the truth (0.0 to 1.0)
- **Confidence**: Confidence in the strength estimate (0.0 to 1.0)

## Quick Start

### Python

```python
from llama_cloud_services import CognitiveAgent

# Create an autonomous agent
agent = CognitiveAgent(name="my_agent")

# Define goals
agent.add_goal("help user", priority=0.9)
agent.add_goal("learn continuously", priority=0.7)

# Register available actions
agent.add_action("search knowledge base", success_prob=0.8)
agent.add_action("generate response", success_prob=0.7)

# Process observations
observations = [
    {"concept": "user needs help", "strength": 0.9, "confidence": 0.9},
    {"concept": "information available", "strength": 0.8, "confidence": 0.8},
]
agent.perceive(observations)

# Run cognitive cycle (perceive -> reason -> act)
result = agent.cognitive_cycle(observations)
print(result)
```

### TypeScript

```typescript
import { CognitiveAgent } from "llama-cloud-services";

// Create an autonomous agent
const agent = new CognitiveAgent("my_agent");

// Define goals
agent.addGoal("help user", 0.9);
agent.addGoal("learn continuously", 0.7);

// Register available actions
agent.addAction("search knowledge base", 0.8);
agent.addAction("generate response", 0.7);

// Process observations
const observations = [
  { concept: "user needs help", strength: 0.9, confidence: 0.9 },
  { concept: "information available", strength: 0.8, confidence: 0.8 },
];
agent.perceive(observations);

// Run cognitive cycle (perceive -> reason -> act)
const result = agent.cognitiveCycle(observations);
console.log(result);
```

## AtomSpace Knowledge Graph

The AtomSpace provides a flexible knowledge representation system:

### Python

```python
from llama_cloud_services import AtomSpace, AtomType, TruthValue

# Create knowledge graph
atomspace = AtomSpace(name="my_knowledge")

# Add atoms
belief = atomspace.add_belief(
    "Python is useful",
    strength=0.9,
    confidence=0.8
)

goal = atomspace.add_goal(
    "learn Python",
    priority=0.85
)

action = atomspace.add_action(
    "study tutorial",
    success_prob=0.7
)

# Link atoms (create relationships)
atomspace.link_atoms(action.id, goal.id)

# Query knowledge
beliefs = atomspace.find_atoms(
    atom_type=AtomType.BELIEF,
    min_strength=0.7
)

# Get related atoms
related = atomspace.get_related_atoms(belief.id)
```

### TypeScript

```typescript
import { AtomSpace, AtomType } from "llama-cloud-services";

// Create knowledge graph
const atomspace = new AtomSpace("my_knowledge");

// Add atoms
const belief = atomspace.addBelief(
  "Python is useful",
  0.9,
  0.8
);

const goal = atomspace.addGoal(
  "learn Python",
  0.85
);

const action = atomspace.addAction(
  "study tutorial",
  0.7
);

// Link atoms (create relationships)
atomspace.linkAtoms(action.id, goal.id);

// Query knowledge
const beliefs = atomspace.findAtoms({
  atomType: AtomType.BELIEF,
  minStrength: 0.7
});

// Get related atoms
const related = atomspace.getRelatedAtoms(belief.id);
```

### Atom Types

- **CONCEPT**: Abstract concepts and entities
- **BELIEF**: Agent's beliefs about the world
- **GOAL**: Agent's goals and objectives
- **ACTION**: Actions the agent can perform
- **IMPLICATION**: Logical implications (if-then rules)
- **EXECUTION**: Planned action executions
- **PREDICATE**: Properties and relations
- **EVALUATION**: Evaluated predicates

## Cognitive Processes

### Perception Process

Transforms observations into knowledge:

```python
from llama_cloud_services import PerceptionProcess, AtomSpace

process = PerceptionProcess()
atomspace = AtomSpace()

observations = [
    {"concept": "user question", "strength": 0.9},
    {"concept": "context provided", "strength": 0.8},
]

result = process.process(atomspace, {"observations": observations})
# Adds beliefs to atomspace based on observations
```

### Reasoning Process

Performs inference over knowledge:

```python
from llama_cloud_services import ReasoningProcess, AtomSpace

process = ReasoningProcess(inference_threshold=0.6)
atomspace = AtomSpace()

# Add knowledge
atomspace.add_belief("user needs help", strength=0.9)
atomspace.add_goal("help user", priority=0.9)

# Reason about knowledge
result = process.process(atomspace, {})
# Creates implications connecting beliefs to goals
```

### Action Process

Selects actions to achieve goals:

```python
from llama_cloud_services import ActionProcess, AtomSpace

process = ActionProcess(action_threshold=0.5)
atomspace = AtomSpace()

# Add goals and actions
atomspace.add_goal("complete task", priority=0.9)
atomspace.add_action("execute task", success_prob=0.8)

# Plan actions
result = process.process(atomspace, {})
# Selects best actions for active goals
```

## Cognitive Agent

The CognitiveAgent combines all components into an autonomous agent:

```python
from llama_cloud_services import CognitiveAgent

agent = CognitiveAgent(
    name="assistant",
    collection="my_agents",
    deployment_name="production"
)

# Setup agent
agent.add_goal("understand user intent", priority=0.95)
agent.add_goal("provide accurate information", priority=0.90)
agent.add_goal("maintain conversation context", priority=0.75)

agent.add_action("search knowledge base", success_prob=0.85)
agent.add_action("generate explanation", success_prob=0.80)
agent.add_action("ask clarification", success_prob=0.90)

agent.add_belief("users prefer concise answers", strength=0.85)
agent.add_belief("examples improve understanding", strength=0.90)

# Run autonomously
observations = [
    {"concept": "user question received", "strength": 0.9},
    {"concept": "topic: Python functions", "strength": 0.85},
]

cycle_result = agent.cognitive_cycle(observations)

# Inspect selected actions
for action in cycle_result["cycle_results"]["action_planning"]["selected_actions"]:
    print(f"Action: {action['action']}")
    print(f"Goal: {action['goal']}")
    print(f"Confidence: {action['score']}")
```

### Agent Methods

- `add_goal(goal, priority)`: Add a goal for the agent
- `add_belief(belief, strength, confidence)`: Add a belief
- `add_action(action, success_prob)`: Register an action
- `perceive(observations)`: Process observations
- `reason()`: Perform reasoning
- `plan_actions()`: Select actions for goals
- `cognitive_cycle(observations)`: Run complete cycle
- `get_knowledge_summary()`: Get knowledge statistics
- `export_knowledge()`: Export knowledge graph

## Integration with LlamaCloud

The cognitive agent can persist its state to LlamaCloud:

```python
from llama_cloud_services import CognitiveAgent
from llama_cloud_services.beta.agent_data.client import AsyncAgentDataClient
from llama_cloud import AsyncLlamaCloud

# Create agent with cloud persistence
agent = CognitiveAgent(
    name="cloud_agent",
    deployment_name="my_deployment",
    collection="cognitive_agents"
)

# Setup cloud client
cloud_client = AsyncLlamaCloud(token="your-api-key")
agent_data_client = AsyncAgentDataClient(
    client=cloud_client,
    type=dict,
    collection="cognitive_agents",
    deployment_name="my_deployment"
)

# Sync to cloud
await agent.sync_to_cloud(agent_data_client)

# Load from cloud
await agent.load_from_cloud(agent_data_client, "agent_id")
```

## Examples

### Simple Assistant Agent

```python
from llama_cloud_services import CognitiveAgent

# Create assistant
assistant = CognitiveAgent(name="helpful_assistant")

# Define purpose
assistant.add_goal("help users learn", priority=0.95)
assistant.add_action("provide explanation", success_prob=0.85)
assistant.add_action("show example", success_prob=0.80)

# React to user
observations = [{"concept": "user needs help with loops", "strength": 0.9}]
result = assistant.cognitive_cycle(observations)

# Check what the agent plans to do
actions = result["cycle_results"]["action_planning"]["selected_actions"]
print(f"Assistant plans to: {actions[0]['action']}")
```

### Research Agent

```python
from llama_cloud_services import CognitiveAgent

# Create research agent
researcher = CognitiveAgent(name="research_agent")

# Define research goals
researcher.add_goal("find relevant information", priority=0.90)
researcher.add_goal("verify information accuracy", priority=0.95)
researcher.add_goal("synthesize findings", priority=0.80)

# Define research capabilities
researcher.add_action("search databases", success_prob=0.85)
researcher.add_action("cross-reference sources", success_prob=0.80)
researcher.add_action("summarize findings", success_prob=0.75)

# Add domain knowledge
researcher.add_belief("primary sources are most reliable", strength=0.95)
researcher.add_belief("multiple sources increase confidence", strength=0.90)

# Execute research cycle
research_query = [
    {"concept": "research topic: AI ethics", "strength": 0.9},
    {"concept": "academic sources available", "strength": 0.85},
]

result = researcher.cognitive_cycle(research_query)
```

### Multi-Goal Agent

```python
from llama_cloud_services import CognitiveAgent

agent = CognitiveAgent(name="multi_goal_agent")

# Multiple competing goals
agent.add_goal("maximize efficiency", priority=0.85)
agent.add_goal("maintain quality", priority=0.90)
agent.add_goal("minimize cost", priority=0.70)

# The agent will balance these goals when selecting actions
agent.add_action("fast processing", success_prob=0.8)
agent.add_action("thorough analysis", success_prob=0.85)
agent.add_action("incremental approach", success_prob=0.75)

# Process situation
situation = [
    {"concept": "large dataset to process", "strength": 0.9},
    {"concept": "accuracy is critical", "strength": 0.85},
    {"concept": "time constraints exist", "strength": 0.70},
]

result = agent.cognitive_cycle(situation)

# Agent will select actions that best balance all goals
```

## Tips & Best Practices

1. **Goal Prioritization**: Use priority values to indicate goal importance (0.0 to 1.0)
2. **Truth Values**: Higher confidence values indicate more reliable knowledge
3. **Action Probabilities**: Set realistic success probabilities for actions
4. **Cognitive Cycles**: Run cycles periodically to keep agent responsive
5. **Knowledge Pruning**: Periodically remove low-confidence, outdated atoms
6. **Cloud Sync**: Persist important agent states to LlamaCloud
7. **Custom Processes**: Extend cognitive processes for domain-specific reasoning

## Advanced Usage

### Custom Cognitive Process

```python
from llama_cloud_services.opencog.cognitive_processes import CognitiveProcess
from llama_cloud_services.opencog.atomspace import AtomSpace

class CustomProcess(CognitiveProcess):
    name: str = "custom"
    
    def process(self, atomspace: AtomSpace, context: dict):
        # Implement custom cognitive logic
        return {"process": self.name, "result": "custom_result"}

# Use custom process
agent = CognitiveAgent(
    name="custom_agent",
    processes=[CustomProcess(), PerceptionProcess(), ActionProcess()]
)
```

### Knowledge Graph Analysis

```python
# Export and analyze knowledge graph
knowledge = agent.export_knowledge()
atomspace_data = knowledge["atomspace"]

# Analyze atom distribution
from collections import Counter
atom_types = Counter(atom["type"] for atom in atomspace_data["atoms"].values())
print(f"Knowledge composition: {atom_types}")

# Find high-confidence knowledge
high_conf_atoms = [
    atom for atom in atomspace_data["atoms"].values()
    if atom["truth_value"]["confidence"] > 0.8
]
```

## Additional Resources

- [OpenCog Framework Documentation](https://wiki.opencog.org)
- [LlamaCloud Services Documentation](https://docs.cloud.llamaindex.ai)
- **Python Examples**: [examples/opencog_agent_example.py](./examples/opencog_agent_example.py)
- **TypeScript Examples**: [examples-ts/opencog-agent-example.ts](./examples-ts/opencog-agent-example.ts)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.
