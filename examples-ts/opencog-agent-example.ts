/**
 * Example: Using OpenCog-inspired Cognitive Agent with LlamaCloud Services
 * 
 * This example demonstrates how to use the CognitiveAgent to create an
 * autonomous agent with goals, beliefs, and reasoning capabilities.
 */

import {
  CognitiveAgent,
  AtomSpace,
  AtomType,
} from "llama-cloud-services";

/**
 * Basic example of creating and using a cognitive agent.
 */
function basicCognitiveAgentExample() {
  console.log("=".repeat(60));
  console.log("Basic Cognitive Agent Example");
  console.log("=".repeat(60));

  // Create a cognitive agent
  const agent = new CognitiveAgent("assistant_agent");

  // Define goals for the agent
  console.log("\n1. Setting agent goals...");
  agent.addGoal("help user with Python", 0.9);
  agent.addGoal("learn new information", 0.7);
  agent.addGoal("improve responses", 0.6);

  // Add available actions
  console.log("2. Registering available actions...");
  agent.addAction("search documentation", 0.8);
  agent.addAction("provide code example", 0.7);
  agent.addAction("ask clarifying question", 0.9);

  // Process observations
  console.log("3. Processing observations...");
  const observations = [
    { concept: "user needs help with Python functions", strength: 0.9, confidence: 0.9 },
    { concept: "user is a beginner", strength: 0.7, confidence: 0.8 },
    { concept: "documentation is available", strength: 0.8, confidence: 0.9 },
  ];
  const perceptionResult = agent.perceive(observations);
  console.log(`   Perceived ${perceptionResult.count} concepts`);

  // Run reasoning process
  console.log("4. Running reasoning process...");
  const reasoningResult = agent.reason();
  console.log(`   Considered ${reasoningResult.beliefsConsidered} beliefs`);
  console.log(`   Evaluated ${reasoningResult.goalsConsidered} goals`);

  // Plan actions
  console.log("5. Planning actions...");
  const actionResult = agent.planActions();
  console.log(`   Selected ${actionResult.selectedActions.length} actions`);
  for (const action of actionResult.selectedActions) {
    console.log(`   - ${action.action} (score: ${action.score.toFixed(2)})`);
  }

  // Get knowledge summary
  console.log("\n6. Agent knowledge summary:");
  const summary = agent.getKnowledgeSummary();
  console.log(`   Total atoms: ${summary.totalAtoms}`);
  console.log(`   Goals: ${summary.goals}`);
  console.log(`   Actions: ${summary.actions}`);
  console.log(`   Implications: ${summary.implications}`);
}

/**
 * Example of running a complete cognitive cycle.
 */
function cognitiveCycleExample() {
  console.log("\n" + "=".repeat(60));
  console.log("Cognitive Cycle Example");
  console.log("=".repeat(60));

  const agent = new CognitiveAgent("learning_agent");

  // Setup
  agent.addGoal("understand user intent", 0.9);
  agent.addGoal("provide helpful response", 0.8);
  agent.addAction("analyze input", 0.85);
  agent.addAction("generate response", 0.75);

  // Run cognitive cycle with new observations
  const observations = [
    { concept: "user asking about lists", strength: 0.9 },
    { concept: "user confused about syntax", strength: 0.7 },
  ];

  console.log("\nRunning cognitive cycle...");
  const result = agent.cognitiveCycle(observations);

  console.log(`\nAgent: ${result.agent}`);
  console.log("\nCycle results:");
  for (const [processName, processResult] of Object.entries(result.cycleResults)) {
    console.log(`  ${processName}:`);
    if (typeof processResult === "object" && processResult !== null) {
      for (const [key, value] of Object.entries(processResult)) {
        if (key !== "process") {
          console.log(`    - ${key}: ${JSON.stringify(value)}`);
        }
      }
    }
  }
}

/**
 * Example of working with the AtomSpace knowledge graph.
 */
function knowledgeGraphExample() {
  console.log("\n" + "=".repeat(60));
  console.log("Knowledge Graph Example");
  console.log("=".repeat(60));

  const agent = new CognitiveAgent("knowledge_agent");

  // Build knowledge graph
  console.log("\n1. Building knowledge graph...");

  // Add concepts using AtomType
  const concept1 = agent.atomspace.addAtom(
    AtomType.CONCEPT,
    "Python programming"
  );

  // Add beliefs
  const belief1 = agent.addBelief("Python is beginner-friendly", 0.9);
  const belief2 = agent.addBelief("Python has great libraries", 0.95);

  // Add goals
  const goal1 = agent.addGoal("teach Python effectively", 0.9);

  console.log("   Added beliefs, goals, and concepts");

  // Query knowledge graph
  console.log("\n2. Querying knowledge graph...");

  const beliefs = agent.atomspace.findAtoms({ atomType: AtomType.BELIEF });
  console.log(`   Found ${beliefs.length} beliefs:`);
  for (const belief of beliefs) {
    console.log(`   - ${belief.name} (strength: ${belief.truthValue.strength.toFixed(2)})`);
  }

  const goals = agent.atomspace.findAtoms({ atomType: AtomType.GOAL });
  console.log(`\n   Found ${goals.length} goals:`);
  for (const goal of goals) {
    console.log(`   - ${goal.name} (priority: ${goal.truthValue.strength.toFixed(2)})`);
  }
}

/**
 * Example of an autonomous agent scenario.
 */
function autonomousAgentScenario() {
  console.log("\n" + "=".repeat(60));
  console.log("Autonomous Agent Scenario");
  console.log("=".repeat(60));

  // Create an agent with specific purpose
  const agent = new CognitiveAgent("tutorial_assistant");

  // Define agent's goals
  agent.addGoal("help user learn Python", 0.95);
  agent.addGoal("provide clear examples", 0.85);
  agent.addGoal("maintain user engagement", 0.75);

  // Define agent's capabilities
  agent.addAction("provide code example", 0.9);
  agent.addAction("explain concept", 0.85);
  agent.addAction("suggest practice exercise", 0.8);
  agent.addAction("recommend resources", 0.75);

  // Initial beliefs
  agent.addBelief("users learn best by doing", 0.9);
  agent.addBelief("examples clarify concepts", 0.85);

  console.log("\nAgent initialized with goals, actions, and beliefs");

  // Simulate interaction over multiple cycles
  const scenarios = [
    {
      name: "User asks about functions",
      observations: [
        { concept: "user interested in functions", strength: 0.9 },
        { concept: "user needs examples", strength: 0.8 },
      ],
    },
    {
      name: "User practices code",
      observations: [
        { concept: "user writing code", strength: 0.85 },
        { concept: "user making progress", strength: 0.7 },
      ],
    },
    {
      name: "User needs clarification",
      observations: [
        { concept: "user confused", strength: 0.8 },
        { concept: "concept needs explanation", strength: 0.9 },
      ],
    },
  ];

  scenarios.forEach((scenario, i) => {
    console.log(`\n--- Cycle ${i + 1}: ${scenario.name} ---`);
    const result = agent.cognitiveCycle(scenario.observations);

    // Show selected actions
    const actions = result.cycleResults.actionPlanning?.selectedActions || [];
    if (actions.length > 0) {
      console.log(`Agent selects: ${actions[0].action}`);
      console.log(`  For goal: ${actions[0].goal}`);
      console.log(`  Confidence: ${actions[0].score.toFixed(2)}`);
    } else {
      console.log("Agent: No action needed at this time");
    }
  });
}

/**
 * Run all examples.
 */
function main() {
  console.log("\n" + "=".repeat(60));
  console.log("OpenCog Cognitive Agent Examples");
  console.log("LlamaCloud Services Integration");
  console.log("=".repeat(60));

  try {
    basicCognitiveAgentExample();
    cognitiveCycleExample();
    knowledgeGraphExample();
    autonomousAgentScenario();

    console.log("\n" + "=".repeat(60));
    console.log("All examples completed successfully!");
    console.log("=".repeat(60));
  } catch (error) {
    console.error("\nError running examples:", error);
    if (error instanceof Error) {
      console.error(error.stack);
    }
  }
}

// Run if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export {
  basicCognitiveAgentExample,
  cognitiveCycleExample,
  knowledgeGraphExample,
  autonomousAgentScenario,
  main,
};
