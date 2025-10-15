"""
AtomSpace: Knowledge graph for storing and managing agent knowledge.

Inspired by OpenCog's AtomSpace, this provides a graph-based knowledge
representation system for autonomous agents.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class AtomType(str, Enum):
    """Types of atoms in the knowledge graph."""

    CONCEPT = "concept"
    PREDICATE = "predicate"
    EVALUATION = "evaluation"
    IMPLICATION = "implication"
    EXECUTION = "execution"
    GOAL = "goal"
    BELIEF = "belief"
    ACTION = "action"


class TruthValue(BaseModel):
    """Probabilistic truth value for knowledge representation."""

    strength: float = Field(
        ge=0.0, le=1.0, description="Confidence in the truth of the atom"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the strength estimate"
    )


class Atom(BaseModel):
    """Basic unit of knowledge in the AtomSpace."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AtomType
    name: str
    truth_value: TruthValue = Field(default_factory=lambda: TruthValue(strength=0.5, confidence=0.5))
    incoming: List[str] = Field(default_factory=list, description="Atoms pointing to this atom")
    outgoing: List[str] = Field(default_factory=list, description="Atoms this atom points to")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_truth_value(self, new_strength: float, new_confidence: float) -> None:
        """Update the truth value with new evidence."""
        # Simple averaging - could be replaced with more sophisticated evidence combination
        old_tv = self.truth_value
        weight_old = old_tv.confidence
        weight_new = new_confidence
        total_weight = weight_old + weight_new
        
        if total_weight > 0:
            self.truth_value.strength = (
                old_tv.strength * weight_old + new_strength * weight_new
            ) / total_weight
            self.truth_value.confidence = min(1.0, total_weight)
        
        self.updated_at = datetime.now()


class AtomSpace(BaseModel):
    """
    Knowledge graph for storing and querying agent knowledge.
    
    This is inspired by OpenCog's AtomSpace and provides a graph-based
    representation of knowledge with probabilistic truth values.
    """

    atoms: Dict[str, Atom] = Field(default_factory=dict)
    name: str = Field(default="default")

    def add_atom(
        self,
        atom_type: AtomType,
        name: str,
        truth_value: Optional[TruthValue] = None,
        outgoing: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Atom:
        """Add a new atom to the AtomSpace."""
        # Check if atom already exists
        for existing_atom in self.atoms.values():
            if existing_atom.type == atom_type and existing_atom.name == name:
                # Update existing atom if truth value provided
                if truth_value:
                    existing_atom.update_truth_value(
                        truth_value.strength, truth_value.confidence
                    )
                return existing_atom

        # Create new atom
        atom = Atom(
            type=atom_type,
            name=name,
            truth_value=truth_value or TruthValue(strength=0.5, confidence=0.5),
            outgoing=outgoing or [],
            metadata=metadata or {},
        )

        self.atoms[atom.id] = atom

        # Update incoming links for outgoing atoms
        for outgoing_id in atom.outgoing:
            if outgoing_id in self.atoms:
                self.atoms[outgoing_id].incoming.append(atom.id)

        return atom

    def get_atom(self, atom_id: str) -> Optional[Atom]:
        """Retrieve an atom by ID."""
        return self.atoms.get(atom_id)

    def find_atoms(
        self,
        atom_type: Optional[AtomType] = None,
        name: Optional[str] = None,
        min_strength: Optional[float] = None,
    ) -> List[Atom]:
        """Find atoms matching specified criteria."""
        results = []
        for atom in self.atoms.values():
            if atom_type and atom.type != atom_type:
                continue
            if name and atom.name != name:
                continue
            if min_strength and atom.truth_value.strength < min_strength:
                continue
            results.append(atom)
        return results

    def add_belief(self, belief: str, strength: float = 0.8, confidence: float = 0.7) -> Atom:
        """Add a belief to the knowledge base."""
        return self.add_atom(
            atom_type=AtomType.BELIEF,
            name=belief,
            truth_value=TruthValue(strength=strength, confidence=confidence),
        )

    def add_goal(self, goal: str, priority: float = 0.5) -> Atom:
        """Add a goal for the agent to pursue."""
        return self.add_atom(
            atom_type=AtomType.GOAL,
            name=goal,
            truth_value=TruthValue(strength=priority, confidence=1.0),
            metadata={"priority": priority, "status": "active"},
        )

    def add_action(self, action: str, success_prob: float = 0.5) -> Atom:
        """Add an action the agent can take."""
        return self.add_atom(
            atom_type=AtomType.ACTION,
            name=action,
            truth_value=TruthValue(strength=success_prob, confidence=0.5),
        )

    def link_atoms(self, source_id: str, target_id: str) -> bool:
        """Create a link between two atoms."""
        if source_id not in self.atoms or target_id not in self.atoms:
            return False

        source = self.atoms[source_id]
        if target_id not in source.outgoing:
            source.outgoing.append(target_id)
            self.atoms[target_id].incoming.append(source_id)
        return True

    def get_related_atoms(self, atom_id: str) -> Dict[str, List[Atom]]:
        """Get atoms related to the given atom."""
        if atom_id not in self.atoms:
            return {"incoming": [], "outgoing": []}

        atom = self.atoms[atom_id]
        return {
            "incoming": [self.atoms[aid] for aid in atom.incoming if aid in self.atoms],
            "outgoing": [self.atoms[aid] for aid in atom.outgoing if aid in self.atoms],
        }

    def to_dict(self) -> Dict[str, Any]:
        """Export AtomSpace to dictionary format."""
        return {
            "name": self.name,
            "atoms": {
                atom_id: atom.model_dump(mode="json")
                for atom_id, atom in self.atoms.items()
            },
        }
