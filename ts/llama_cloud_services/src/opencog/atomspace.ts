/**
 * AtomSpace: Knowledge graph for storing and managing agent knowledge.
 * 
 * Inspired by OpenCog's AtomSpace, this provides a graph-based knowledge
 * representation system for autonomous agents.
 */

/**
 * Types of atoms in the knowledge graph.
 */
export enum AtomType {
  CONCEPT = "concept",
  PREDICATE = "predicate",
  EVALUATION = "evaluation",
  IMPLICATION = "implication",
  EXECUTION = "execution",
  GOAL = "goal",
  BELIEF = "belief",
  ACTION = "action",
}

/**
 * Probabilistic truth value for knowledge representation.
 */
export interface TruthValue {
  /** Confidence in the truth of the atom (0.0 to 1.0) */
  strength: number;
  /** Confidence in the strength estimate (0.0 to 1.0) */
  confidence: number;
}

/**
 * Basic unit of knowledge in the AtomSpace.
 */
export interface Atom {
  id: string;
  type: AtomType;
  name: string;
  truthValue: TruthValue;
  /** Atoms pointing to this atom */
  incoming: string[];
  /** Atoms this atom points to */
  outgoing: string[];
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Knowledge graph for storing and querying agent knowledge.
 * 
 * This is inspired by OpenCog's AtomSpace and provides a graph-based
 * representation of knowledge with probabilistic truth values.
 */
export class AtomSpace {
  atoms: Map<string, Atom> = new Map();
  name: string;

  constructor(name: string = "default") {
    this.name = name;
  }

  /**
   * Generate a unique ID for an atom.
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Update truth value with new evidence.
   */
  private updateTruthValue(
    atom: Atom,
    newStrength: number,
    newConfidence: number
  ): void {
    const oldTv = atom.truthValue;
    const weightOld = oldTv.confidence;
    const weightNew = newConfidence;
    const totalWeight = weightOld + weightNew;

    if (totalWeight > 0) {
      atom.truthValue.strength =
        (oldTv.strength * weightOld + newStrength * weightNew) / totalWeight;
      atom.truthValue.confidence = Math.min(1.0, totalWeight);
    }

    atom.updatedAt = new Date();
  }

  /**
   * Add a new atom to the AtomSpace.
   */
  addAtom(
    atomType: AtomType,
    name: string,
    truthValue?: TruthValue,
    outgoing?: string[],
    metadata?: Record<string, any>
  ): Atom {
    // Check if atom already exists
    for (const existingAtom of this.atoms.values()) {
      if (existingAtom.type === atomType && existingAtom.name === name) {
        // Update existing atom if truth value provided
        if (truthValue) {
          this.updateTruthValue(
            existingAtom,
            truthValue.strength,
            truthValue.confidence
          );
        }
        return existingAtom;
      }
    }

    // Create new atom
    const atom: Atom = {
      id: this.generateId(),
      type: atomType,
      name,
      truthValue: truthValue || { strength: 0.5, confidence: 0.5 },
      incoming: [],
      outgoing: outgoing || [],
      metadata: metadata || {},
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.atoms.set(atom.id, atom);

    // Update incoming links for outgoing atoms
    for (const outgoingId of atom.outgoing) {
      const outgoingAtom = this.atoms.get(outgoingId);
      if (outgoingAtom) {
        outgoingAtom.incoming.push(atom.id);
      }
    }

    return atom;
  }

  /**
   * Retrieve an atom by ID.
   */
  getAtom(atomId: string): Atom | undefined {
    return this.atoms.get(atomId);
  }

  /**
   * Find atoms matching specified criteria.
   */
  findAtoms(options?: {
    atomType?: AtomType;
    name?: string;
    minStrength?: number;
  }): Atom[] {
    const results: Atom[] = [];

    for (const atom of this.atoms.values()) {
      if (options?.atomType && atom.type !== options.atomType) {
        continue;
      }
      if (options?.name && atom.name !== options.name) {
        continue;
      }
      if (
        options?.minStrength !== undefined &&
        atom.truthValue.strength < options.minStrength
      ) {
        continue;
      }
      results.push(atom);
    }

    return results;
  }

  /**
   * Add a belief to the knowledge base.
   */
  addBelief(belief: string, strength: number = 0.8, confidence: number = 0.7): Atom {
    return this.addAtom(AtomType.BELIEF, belief, { strength, confidence });
  }

  /**
   * Add a goal for the agent to pursue.
   */
  addGoal(goal: string, priority: number = 0.5): Atom {
    return this.addAtom(
      AtomType.GOAL,
      goal,
      { strength: priority, confidence: 1.0 },
      undefined,
      { priority, status: "active" }
    );
  }

  /**
   * Add an action the agent can take.
   */
  addAction(action: string, successProb: number = 0.5): Atom {
    return this.addAtom(AtomType.ACTION, action, {
      strength: successProb,
      confidence: 0.5,
    });
  }

  /**
   * Create a link between two atoms.
   */
  linkAtoms(sourceId: string, targetId: string): boolean {
    const source = this.atoms.get(sourceId);
    const target = this.atoms.get(targetId);

    if (!source || !target) {
      return false;
    }

    if (!source.outgoing.includes(targetId)) {
      source.outgoing.push(targetId);
      target.incoming.push(sourceId);
    }

    return true;
  }

  /**
   * Get atoms related to the given atom.
   */
  getRelatedAtoms(atomId: string): {
    incoming: Atom[];
    outgoing: Atom[];
  } {
    const atom = this.atoms.get(atomId);

    if (!atom) {
      return { incoming: [], outgoing: [] };
    }

    return {
      incoming: atom.incoming
        .map((id) => this.atoms.get(id))
        .filter((a): a is Atom => a !== undefined),
      outgoing: atom.outgoing
        .map((id) => this.atoms.get(id))
        .filter((a): a is Atom => a !== undefined),
    };
  }

  /**
   * Export AtomSpace to plain object format.
   */
  toDict(): {
    name: string;
    atoms: Record<string, any>;
  } {
    const atomsDict: Record<string, any> = {};

    for (const [atomId, atom] of this.atoms.entries()) {
      atomsDict[atomId] = {
        id: atom.id,
        type: atom.type,
        name: atom.name,
        truthValue: atom.truthValue,
        incoming: atom.incoming,
        outgoing: atom.outgoing,
        metadata: atom.metadata,
        createdAt: atom.createdAt.toISOString(),
        updatedAt: atom.updatedAt.toISOString(),
      };
    }

    return {
      name: this.name,
      atoms: atomsDict,
    };
  }
}
