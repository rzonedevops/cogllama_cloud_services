/**
 * Cognitive processes for autonomous agents.
 * 
 * Inspired by OpenCog's cognitive architecture, this module implements
 * perception, reasoning, and action processes.
 */

import { AtomSpace, Atom, AtomType, TruthValue } from "./atomspace.js";

/**
 * Base interface for cognitive processes.
 */
export interface CognitiveProcess {
  name: string;
  enabled: boolean;
  process(atomspace: AtomSpace, context: Record<string, any>): Record<string, any>;
}

/**
 * Perception process: Transform sensory input into knowledge.
 * 
 * This process takes external observations and adds them to the
 * agent's knowledge base (AtomSpace) as beliefs.
 */
export class PerceptionProcess implements CognitiveProcess {
  name: string = "perception";
  enabled: boolean = true;

  process(atomspace: AtomSpace, context: Record<string, any>): Record<string, any> {
    const observations = context.observations || [];
    const perceivedConcepts: string[] = [];

    for (const observation of observations) {
      let conceptName: string;
      let strength: number;
      let confidence: number;

      if (typeof observation === "object" && observation !== null) {
        conceptName = observation.concept || "unknown";
        strength = observation.strength ?? 0.7;
        confidence = observation.confidence ?? 0.8;
      } else {
        conceptName = String(observation);
        strength = 0.7;
        confidence = 0.8;
      }

      // Add perception as belief
      const atom = atomspace.addBelief(
        `perceived:${conceptName}`,
        strength,
        confidence
      );
      perceivedConcepts.push(atom.id);
    }

    return {
      process: this.name,
      perceivedConcepts,
      count: perceivedConcepts.length,
    };
  }
}

/**
 * Reasoning process: Infer new knowledge from existing knowledge.
 * 
 * This process performs logical inference, pattern matching, and
 * knowledge integration to derive new beliefs and implications.
 */
export class ReasoningProcess implements CognitiveProcess {
  name: string = "reasoning";
  enabled: boolean = true;
  inferenceThreshold: number;

  constructor(inferenceThreshold: number = 0.6) {
    this.inferenceThreshold = inferenceThreshold;
  }

  process(atomspace: AtomSpace, context: Record<string, any>): Record<string, any> {
    const inferences: string[] = [];

    // Find high-confidence beliefs
    const beliefs = atomspace.findAtoms({
      atomType: AtomType.BELIEF,
      minStrength: this.inferenceThreshold,
    });

    // Find active goals
    const goals = atomspace.findAtoms({ atomType: AtomType.GOAL });

    // Simple goal-belief matching reasoning
    for (const goal of goals) {
      if (goal.metadata.status !== "active") {
        continue;
      }

      for (const belief of beliefs) {
        // Check if belief is relevant to goal
        if (this.isRelevant(goal.name, belief.name)) {
          // Create implication: belief -> goal achievable
          const truthValue: TruthValue = {
            strength: Math.min(belief.truthValue.strength, 0.8),
            confidence: belief.truthValue.confidence * 0.8,
          };

          const implication = atomspace.addAtom(
            AtomType.IMPLICATION,
            `${belief.name} => ${goal.name}`,
            truthValue,
            [belief.id, goal.id]
          );
          inferences.push(implication.id);
        }
      }
    }

    return {
      process: this.name,
      inferences,
      beliefsConsidered: beliefs.length,
      goalsConsidered: goals.length,
    };
  }

  private isRelevant(goalName: string, beliefName: string): boolean {
    // Simple keyword-based relevance
    const goalWords = new Set(goalName.toLowerCase().split(/\s+/));
    const beliefWords = new Set(beliefName.toLowerCase().split(/\s+/));

    for (const word of goalWords) {
      if (beliefWords.has(word)) {
        return true;
      }
    }
    return false;
  }
}

/**
 * Action process: Select and execute actions to achieve goals.
 * 
 * This process evaluates potential actions based on goals, beliefs,
 * and expected outcomes, then selects the most promising action.
 */
export class ActionProcess implements CognitiveProcess {
  name: string = "action";
  enabled: boolean = true;
  actionThreshold: number;

  constructor(actionThreshold: number = 0.5) {
    this.actionThreshold = actionThreshold;
  }

  process(atomspace: AtomSpace, context: Record<string, any>): Record<string, any> {
    const selectedActions: Array<{
      executionId: string;
      action: string;
      goal: string;
      score: number;
    }> = [];

    // Find active goals sorted by priority
    const goals = atomspace.findAtoms({ atomType: AtomType.GOAL });
    const activeGoals = goals
      .filter((g) => g.metadata.status === "active")
      .sort((a, b) => b.truthValue.strength - a.truthValue.strength);

    // Find available actions
    const actions = atomspace.findAtoms({ atomType: AtomType.ACTION });

    // For each goal, find relevant actions (consider top 3 goals)
    for (const goal of activeGoals.slice(0, 3)) {
      let bestAction: Atom | null = null;
      let bestScore = 0.0;

      for (const action of actions) {
        // Check if action is relevant to goal
        if (this.actionHelpsGoal(action, goal, atomspace)) {
          const score = this.calculateActionScore(action, goal);
          if (score > bestScore && score >= this.actionThreshold) {
            bestScore = score;
            bestAction = action;
          }
        }
      }

      if (bestAction) {
        // Create execution plan
        const truthValue: TruthValue = {
          strength: bestScore,
          confidence: 0.8,
        };

        const execution = atomspace.addAtom(
          AtomType.EXECUTION,
          `execute:${bestAction.name}`,
          truthValue,
          [bestAction.id, goal.id],
          {
            goalId: goal.id,
            actionId: bestAction.id,
            expectedUtility: bestScore,
          }
        );

        selectedActions.push({
          executionId: execution.id,
          action: bestAction.name,
          goal: goal.name,
          score: bestScore,
        });
      }
    }

    return {
      process: this.name,
      selectedActions,
      goalsAddressed: selectedActions.length,
    };
  }

  private actionHelpsGoal(
    action: Atom,
    goal: Atom,
    atomspace: AtomSpace
  ): boolean {
    // Check for implications linking action to goal
    const implications = atomspace.findAtoms({ atomType: AtomType.IMPLICATION });
    for (const imp of implications) {
      if (
        imp.outgoing.includes(action.id) &&
        imp.outgoing.includes(goal.id)
      ) {
        return true;
      }
    }

    // Fallback: simple name matching
    return this.isRelevant(goal.name, action.name);
  }

  private calculateActionScore(action: Atom, goal: Atom): number {
    // Combine action success probability with goal priority
    const actionStrength = action.truthValue.strength;
    const goalPriority = goal.truthValue.strength;
    return (actionStrength + goalPriority) / 2.0;
  }

  private isRelevant(goalName: string, actionName: string): boolean {
    // Simple keyword-based relevance
    const goalWords = new Set(goalName.toLowerCase().split(/\s+/));
    const actionWords = new Set(actionName.toLowerCase().split(/\s+/));

    for (const word of goalWords) {
      if (actionWords.has(word)) {
        return true;
      }
    }
    return false;
  }
}
