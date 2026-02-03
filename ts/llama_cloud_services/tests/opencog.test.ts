import { describe, it, expect, beforeEach } from "vitest";
import {
  AtomSpace,
  AtomType,
  TruthValue,
  CognitiveAgent,
  PerceptionProcess,
  ReasoningProcess,
  ActionProcess,
} from "../src/opencog/index.js";

describe("OpenCog AtomSpace Tests", () => {
  let atomspace: AtomSpace;

  beforeEach(() => {
    atomspace = new AtomSpace("test_space");
  });

  describe("AtomSpace Creation", () => {
    it("should create an AtomSpace with a name", () => {
      expect(atomspace.name).toBe("test_space");
      expect(atomspace.atoms.size).toBe(0);
    });

    it("should create an AtomSpace with default name", () => {
      const defaultSpace = new AtomSpace();
      expect(defaultSpace.name).toBe("default");
    });
  });

  describe("Atom Operations", () => {
    it("should add a concept atom", () => {
      // Note: Atom names can contain spaces as they represent natural language concepts
      const atom = atomspace.addAtom(AtomType.CONCEPT, "test concept");
      
      expect(atom.type).toBe(AtomType.CONCEPT);
      expect(atom.name).toBe("test concept");
      expect(atom.id).toBeDefined();
      expect(atomspace.atoms.size).toBe(1);
    });

    it("should add atom with custom truth value", () => {
      const truthValue: TruthValue = { strength: 0.9, confidence: 0.8 };
      const atom = atomspace.addAtom(
        AtomType.BELIEF,
        "test belief",
        truthValue
      );

      expect(atom.truthValue.strength).toBe(0.9);
      expect(atom.truthValue.confidence).toBe(0.8);
    });

    it("should update existing atom when adding duplicate", () => {
      const atom1 = atomspace.addAtom(
        AtomType.BELIEF,
        "test",
        { strength: 0.5, confidence: 0.5 }
      );
      const initialId = atom1.id;

      const atom2 = atomspace.addAtom(
        AtomType.BELIEF,
        "test",
        { strength: 0.8, confidence: 0.7 }
      );

      expect(atom2.id).toBe(initialId);
      expect(atomspace.atoms.size).toBe(1);
      expect(atom2.truthValue.strength).toBeGreaterThan(0.5);
    });

    it("should retrieve atom by ID", () => {
      const atom = atomspace.addAtom(AtomType.GOAL, "test goal");
      const retrieved = atomspace.getAtom(atom.id);

      expect(retrieved).toBeDefined();
      expect(retrieved?.name).toBe("test goal");
    });

    it("should return undefined for non-existent atom", () => {
      const retrieved = atomspace.getAtom("non-existent-id");
      expect(retrieved).toBeUndefined();
    });
  });

  describe("Specialized Atom Methods", () => {
    it("should add a belief", () => {
      const belief = atomspace.addBelief("Python is useful", 0.9, 0.8);

      expect(belief.type).toBe(AtomType.BELIEF);
      expect(belief.name).toBe("Python is useful");
      expect(belief.truthValue.strength).toBe(0.9);
      expect(belief.truthValue.confidence).toBe(0.8);
    });

    it("should add a goal", () => {
      const goal = atomspace.addGoal("learn programming", 0.85);

      expect(goal.type).toBe(AtomType.GOAL);
      expect(goal.name).toBe("learn programming");
      expect(goal.truthValue.strength).toBe(0.85);
      expect(goal.metadata.priority).toBe(0.85);
      expect(goal.metadata.status).toBe("active");
    });

    it("should add an action", () => {
      const action = atomspace.addAction("search documentation", 0.7);

      expect(action.type).toBe(AtomType.ACTION);
      expect(action.name).toBe("search documentation");
      expect(action.truthValue.strength).toBe(0.7);
    });
  });

  describe("Atom Linking", () => {
    it("should link two atoms", () => {
      const atom1 = atomspace.addAtom(AtomType.CONCEPT, "concept1");
      const atom2 = atomspace.addAtom(AtomType.CONCEPT, "concept2");

      const success = atomspace.linkAtoms(atom1.id, atom2.id);

      expect(success).toBe(true);
      expect(atom1.outgoing).toContain(atom2.id);
      expect(atom2.incoming).toContain(atom1.id);
    });

    it("should not link non-existent atoms", () => {
      const atom = atomspace.addAtom(AtomType.CONCEPT, "test");
      const success = atomspace.linkAtoms(atom.id, "non-existent");

      expect(success).toBe(false);
    });

    it("should not duplicate links", () => {
      const atom1 = atomspace.addAtom(AtomType.CONCEPT, "concept1");
      const atom2 = atomspace.addAtom(AtomType.CONCEPT, "concept2");

      atomspace.linkAtoms(atom1.id, atom2.id);
      atomspace.linkAtoms(atom1.id, atom2.id);

      expect(atom1.outgoing.length).toBe(1);
      expect(atom2.incoming.length).toBe(1);
    });
  });

  describe("Atom Queries", () => {
    beforeEach(() => {
      atomspace.addBelief("belief1", 0.9);
      atomspace.addBelief("belief2", 0.5);
      atomspace.addGoal("goal1", 0.8);
      atomspace.addAction("action1", 0.7);
    });

    it("should find atoms by type", () => {
      const beliefs = atomspace.findAtoms({ atomType: AtomType.BELIEF });
      expect(beliefs.length).toBe(2);
    });

    it("should find atoms by name", () => {
      const results = atomspace.findAtoms({ name: "belief1" });
      expect(results.length).toBe(1);
      expect(results[0].name).toBe("belief1");
    });

    it("should find atoms by minimum strength", () => {
      const results = atomspace.findAtoms({ minStrength: 0.7 });
      expect(results.length).toBeGreaterThanOrEqual(2);
      results.forEach((atom) => {
        expect(atom.truthValue.strength).toBeGreaterThanOrEqual(0.7);
      });
    });

    it("should combine query criteria", () => {
      const results = atomspace.findAtoms({
        atomType: AtomType.BELIEF,
        minStrength: 0.7,
      });
      expect(results.length).toBe(1);
      expect(results[0].name).toBe("belief1");
    });
  });

  describe("Related Atoms", () => {
    it("should get related atoms", () => {
      const atom1 = atomspace.addAtom(AtomType.CONCEPT, "concept1");
      const atom2 = atomspace.addAtom(AtomType.CONCEPT, "concept2");
      const atom3 = atomspace.addAtom(AtomType.CONCEPT, "concept3");

      atomspace.linkAtoms(atom1.id, atom2.id);
      atomspace.linkAtoms(atom3.id, atom1.id);

      const related = atomspace.getRelatedAtoms(atom1.id);

      expect(related.outgoing.length).toBe(1);
      expect(related.outgoing[0].id).toBe(atom2.id);
      expect(related.incoming.length).toBe(1);
      expect(related.incoming[0].id).toBe(atom3.id);
    });

    it("should return empty arrays for non-existent atom", () => {
      const related = atomspace.getRelatedAtoms("non-existent");
      expect(related.incoming).toEqual([]);
      expect(related.outgoing).toEqual([]);
    });
  });

  describe("AtomSpace Export", () => {
    it("should export to dictionary format", () => {
      atomspace.addBelief("test belief", 0.9);
      atomspace.addGoal("test goal", 0.8);

      const exported = atomspace.toDict();

      expect(exported.name).toBe("test_space");
      expect(Object.keys(exported.atoms).length).toBe(2);
    });
  });
});

describe("OpenCog Cognitive Processes Tests", () => {
  let atomspace: AtomSpace;

  beforeEach(() => {
    atomspace = new AtomSpace("test");
  });

  describe("PerceptionProcess", () => {
    it("should process observations", () => {
      const process = new PerceptionProcess();
      const observations = [
        { concept: "user question", strength: 0.9, confidence: 0.8 },
        { concept: "context available", strength: 0.7, confidence: 0.9 },
      ];

      const result = process.process(atomspace, { observations });

      expect(result.process).toBe("perception");
      expect(result.count).toBe(2);
      expect(result.perceivedConcepts).toHaveLength(2);
    });

    it("should handle string observations", () => {
      const process = new PerceptionProcess();
      const observations = ["test1", "test2"];

      const result = process.process(atomspace, { observations });

      expect(result.count).toBe(2);
    });

    it("should handle empty observations", () => {
      const process = new PerceptionProcess();
      const result = process.process(atomspace, {});

      expect(result.count).toBe(0);
    });
  });

  describe("ReasoningProcess", () => {
    it("should create implications from beliefs and goals", () => {
      const process = new ReasoningProcess(0.5);

      atomspace.addBelief("user needs help", 0.9);
      atomspace.addGoal("help user", 0.9);

      const result = process.process(atomspace, {});

      expect(result.process).toBe("reasoning");
      expect(result.beliefsConsidered).toBeGreaterThan(0);
      expect(result.goalsConsidered).toBeGreaterThan(0);
    });

    it("should respect inference threshold", () => {
      const process = new ReasoningProcess(0.9);

      atomspace.addBelief("low confidence", 0.5);
      atomspace.addGoal("test goal", 0.8);

      const result = process.process(atomspace, {});

      expect(result.beliefsConsidered).toBe(0);
    });
  });

  describe("ActionProcess", () => {
    it("should select actions for goals", () => {
      const process = new ActionProcess(0.4);

      atomspace.addGoal("complete task", 0.9);
      atomspace.addAction("execute task", 0.8);

      const result = process.process(atomspace, {});

      expect(result.process).toBe("action");
      expect(result.selectedActions).toBeDefined();
    });

    it("should respect action threshold", () => {
      const process = new ActionProcess(0.95);

      atomspace.addGoal("test goal", 0.5);
      atomspace.addAction("test action", 0.5);

      const result = process.process(atomspace, {});

      expect(result.selectedActions.length).toBe(0);
    });

    it("should limit to top 3 goals", () => {
      const process = new ActionProcess(0.4);

      for (let i = 0; i < 5; i++) {
        atomspace.addGoal(`goal${i}`, 0.8 - i * 0.1);
        atomspace.addAction(`action${i}`, 0.7);
      }

      const result = process.process(atomspace, {});

      expect(result.goalsAddressed).toBeLessThanOrEqual(3);
    });
  });
});

describe("OpenCog CognitiveAgent Tests", () => {
  let agent: CognitiveAgent;

  beforeEach(() => {
    agent = new CognitiveAgent("test_agent");
  });

  describe("Agent Creation", () => {
    it("should create agent with name", () => {
      expect(agent.name).toBe("test_agent");
      expect(agent.atomspace).toBeDefined();
      expect(agent.processes.length).toBe(3);
    });

    it("should initialize with default processes", () => {
      expect(agent.processes[0]).toBeInstanceOf(PerceptionProcess);
      expect(agent.processes[1]).toBeInstanceOf(ReasoningProcess);
      expect(agent.processes[2]).toBeInstanceOf(ActionProcess);
    });

    it("should accept custom processes", () => {
      const customAgent = new CognitiveAgent("custom", {
        processes: [new PerceptionProcess()],
      });

      expect(customAgent.processes.length).toBe(1);
    });
  });

  describe("Goal Management", () => {
    it("should add a goal", () => {
      const goalId = agent.addGoal("test goal", 0.9);

      expect(goalId).toBeDefined();
      const goals = agent.atomspace.findAtoms({ atomType: AtomType.GOAL });
      expect(goals.length).toBe(1);
      expect(goals[0].name).toBe("test goal");
    });
  });

  describe("Belief Management", () => {
    it("should add a belief", () => {
      const beliefId = agent.addBelief("test belief", 0.8, 0.7);

      expect(beliefId).toBeDefined();
      const beliefs = agent.atomspace.findAtoms({ atomType: AtomType.BELIEF });
      expect(beliefs.length).toBe(1);
    });
  });

  describe("Action Management", () => {
    it("should add an action", () => {
      const actionId = agent.addAction("test action", 0.7);

      expect(actionId).toBeDefined();
      const actions = agent.atomspace.findAtoms({ atomType: AtomType.ACTION });
      expect(actions.length).toBe(1);
    });
  });

  describe("Cognitive Processes", () => {
    it("should perceive observations", () => {
      const observations = [
        { concept: "user question", strength: 0.9 },
      ];

      const result = agent.perceive(observations);

      expect(result.process).toBe("perception");
      expect(result.count).toBe(1);
    });

    it("should perform reasoning", () => {
      agent.addBelief("test belief", 0.9);
      agent.addGoal("test goal", 0.8);

      const result = agent.reason();

      expect(result.process).toBe("reasoning");
      expect(result.beliefsConsidered).toBeGreaterThanOrEqual(0);
    });

    it("should plan actions", () => {
      agent.addGoal("test goal", 0.9);
      agent.addAction("test action", 0.8);

      const result = agent.planActions();

      expect(result.process).toBe("action");
      expect(result.selectedActions).toBeDefined();
    });
  });

  describe("Cognitive Cycle", () => {
    it("should execute complete cognitive cycle", () => {
      agent.addGoal("help user", 0.9);
      agent.addAction("provide help", 0.8);

      const observations = [
        { concept: "user needs help", strength: 0.9 },
      ];

      const result = agent.cognitiveCycle(observations);

      expect(result.agent).toBe("test_agent");
      expect(result.cycleResults.perception).toBeDefined();
      expect(result.cycleResults.reasoning).toBeDefined();
      expect(result.cycleResults.actionPlanning).toBeDefined();
    });

    it("should run cycle without new observations", () => {
      agent.addBelief("existing belief", 0.8);

      const result = agent.cognitiveCycle();

      expect(result.cycleResults.perception).toBeUndefined();
      expect(result.cycleResults.reasoning).toBeDefined();
    });
  });

  describe("Knowledge Summary", () => {
    it("should provide knowledge summary", () => {
      agent.addGoal("goal1", 0.9);
      agent.addBelief("belief1", 0.8);
      agent.addAction("action1", 0.7);

      const summary = agent.getKnowledgeSummary();

      expect(summary.agent).toBe("test_agent");
      expect(summary.totalAtoms).toBeGreaterThan(0);
      expect(summary.goals).toBeGreaterThan(0);
      expect(summary.beliefs).toBeGreaterThan(0);
      expect(summary.actions).toBeGreaterThan(0);
    });
  });

  describe("Knowledge Export", () => {
    it("should export knowledge", () => {
      agent.addGoal("test goal", 0.9);

      const exported = agent.exportKnowledge();

      expect(exported.agent).toBe("test_agent");
      expect(exported.atomspace).toBeDefined();
      expect(exported.processes).toHaveLength(3);
    });
  });
});
