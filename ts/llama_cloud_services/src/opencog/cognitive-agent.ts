/**
 * CognitiveAgent: Autonomous agent with OpenCog-inspired cognitive architecture.
 * 
 * This agent integrates perception, reasoning, and action processes for
 * autonomous operation.
 */

import { AtomSpace, Atom } from "./atomspace.js";
import {
  CognitiveProcess,
  PerceptionProcess,
  ReasoningProcess,
  ActionProcess,
} from "./cognitive-processes.js";

/**
 * Autonomous agent with cognitive architecture.
 * 
 * Integrates OpenCog-inspired cognitive processes for
 * autonomous goal-directed behavior.
 * 
 * @example
 * ```typescript
 * import { CognitiveAgent } from "llama-cloud-services";
 * 
 * // Create agent
 * const agent = new CognitiveAgent("assistant");
 * 
 * // Set goals
 * agent.addGoal("help user", 0.9);
 * agent.addGoal("learn new information", 0.7);
 * 
 * // Process observations
 * const result = agent.perceive([
 *   { concept: "user needs help with Python", strength: 0.9 },
 *   { concept: "documentation available", strength: 0.8 },
 * ]);
 * 
 * // Run cognitive cycle
 * const cycleResult = agent.cognitiveCycle();
 * ```
 */
export class CognitiveAgent {
  name: string;
  atomspace: AtomSpace;
  processes: CognitiveProcess[];
  deploymentName?: string;
  collection: string;

  constructor(
    name: string,
    options?: {
      deploymentName?: string;
      collection?: string;
      processes?: CognitiveProcess[];
    }
  ) {
    this.name = name;
    this.atomspace = new AtomSpace("agent_memory");
    this.deploymentName = options?.deploymentName;
    this.collection = options?.collection || "cognitive_agent";

    // Initialize default cognitive processes
    this.processes = options?.processes || [
      new PerceptionProcess(),
      new ReasoningProcess(),
      new ActionProcess(),
    ];
  }

  /**
   * Add a goal for the agent to pursue.
   */
  addGoal(goal: string, priority: number = 0.5): string {
    const atom = this.atomspace.addGoal(goal, priority);
    return atom.id;
  }

  /**
   * Add a belief to the agent's knowledge base.
   */
  addBelief(belief: string, strength: number = 0.8, confidence: number = 0.7): string {
    const atom = this.atomspace.addBelief(belief, strength, confidence);
    return atom.id;
  }

  /**
   * Register an action the agent can take.
   */
  addAction(action: string, successProb: number = 0.5): string {
    const atom = this.atomspace.addAction(action, successProb);
    return atom.id;
  }

  /**
   * Process sensory observations and update knowledge base.
   * 
   * @param observations - List of observations (object or string)
   * @returns Dictionary with perception results
   */
  perceive(observations: any[]): Record<string, any> {
    const perceptionProcess = this.processes.find(
      (p) => p instanceof PerceptionProcess
    );

    if (!perceptionProcess) {
      return { error: "No perception process available" };
    }

    const context = { observations };
    return perceptionProcess.process(this.atomspace, context);
  }

  /**
   * Perform reasoning over current knowledge base.
   * 
   * @returns Dictionary with reasoning results
   */
  reason(): Record<string, any> {
    const reasoningProcess = this.processes.find(
      (p) => p instanceof ReasoningProcess
    );

    if (!reasoningProcess) {
      return { error: "No reasoning process available" };
    }

    return reasoningProcess.process(this.atomspace, {});
  }

  /**
   * Select actions to achieve goals.
   * 
   * @returns Dictionary with selected actions
   */
  planActions(): Record<string, any> {
    const actionProcess = this.processes.find(
      (p) => p instanceof ActionProcess
    );

    if (!actionProcess) {
      return { error: "No action process available" };
    }

    return actionProcess.process(this.atomspace, {});
  }

  /**
   * Execute a complete cognitive cycle: perceive -> reason -> act.
   * 
   * @param observations - Optional new observations to perceive
   * @returns Dictionary with results from each process
   */
  cognitiveCycle(observations?: any[]): Record<string, any> {
    const results: Record<string, any> = {
      agent: this.name,
      cycleResults: {},
    };

    // Perceive
    if (observations) {
      results.cycleResults.perception = this.perceive(observations);
    }

    // Reason
    results.cycleResults.reasoning = this.reason();

    // Plan actions
    results.cycleResults.actionPlanning = this.planActions();

    return results;
  }

  /**
   * Get a summary of the agent's current knowledge.
   */
  getKnowledgeSummary(): Record<string, any> {
    const atoms = Array.from(this.atomspace.atoms.values());

    return {
      agent: this.name,
      totalAtoms: atoms.length,
      beliefs: atoms.filter((a) => a.type === "belief").length,
      goals: atoms.filter((a) => a.type === "goal").length,
      actions: atoms.filter((a) => a.type === "action").length,
      implications: atoms.filter((a) => a.type === "implication").length,
    };
  }

  /**
   * Export the agent's knowledge base.
   */
  exportKnowledge(): Record<string, any> {
    return {
      agent: this.name,
      atomspace: this.atomspace.toDict(),
      processes: this.processes.map((p) => p.name),
    };
  }
}
