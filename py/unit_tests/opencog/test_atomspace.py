"""Unit tests for AtomSpace knowledge graph."""

import pytest
from llama_cloud_services.opencog.atomspace import (
    AtomSpace,
    Atom,
    AtomType,
    TruthValue,
)


class TestTruthValue:
    """Tests for TruthValue class."""

    def test_truth_value_creation(self):
        tv = TruthValue(strength=0.8, confidence=0.9)
        assert tv.strength == 0.8
        assert tv.confidence == 0.9

    def test_truth_value_bounds(self):
        """Test that values are constrained to [0, 1]."""
        with pytest.raises(Exception):
            TruthValue(strength=1.5, confidence=0.5)
        with pytest.raises(Exception):
            TruthValue(strength=0.5, confidence=-0.1)


class TestAtom:
    """Tests for Atom class."""

    def test_atom_creation(self):
        atom = Atom(
            type=AtomType.CONCEPT,
            name="test_concept",
            truth_value=TruthValue(strength=0.7, confidence=0.8),
        )
        assert atom.type == AtomType.CONCEPT
        assert atom.name == "test_concept"
        assert atom.truth_value.strength == 0.7
        assert atom.id is not None

    def test_atom_update_truth_value(self):
        atom = Atom(
            type=AtomType.BELIEF,
            name="test_belief",
            truth_value=TruthValue(strength=0.5, confidence=0.5),
        )
        original_time = atom.updated_at

        # Update with new evidence
        atom.update_truth_value(0.9, 0.8)

        # Truth value should be updated (weighted average)
        assert atom.truth_value.strength > 0.5
        assert atom.truth_value.confidence > 0.5
        assert atom.updated_at > original_time


class TestAtomSpace:
    """Tests for AtomSpace knowledge graph."""

    def test_atomspace_creation(self):
        atomspace = AtomSpace(name="test_space")
        assert atomspace.name == "test_space"
        assert len(atomspace.atoms) == 0

    def test_add_atom(self):
        atomspace = AtomSpace()
        atom = atomspace.add_atom(
            atom_type=AtomType.CONCEPT,
            name="python",
            truth_value=TruthValue(strength=0.9, confidence=0.8),
        )
        assert atom.type == AtomType.CONCEPT
        assert atom.name == "python"
        assert len(atomspace.atoms) == 1

    def test_add_duplicate_atom(self):
        """Adding same atom twice should update existing atom."""
        atomspace = AtomSpace()
        atom1 = atomspace.add_atom(
            atom_type=AtomType.CONCEPT,
            name="test",
            truth_value=TruthValue(strength=0.5, confidence=0.5),
        )
        atom2 = atomspace.add_atom(
            atom_type=AtomType.CONCEPT,
            name="test",
            truth_value=TruthValue(strength=0.9, confidence=0.8),
        )

        # Should return same atom (updated)
        assert atom1.id == atom2.id
        assert len(atomspace.atoms) == 1
        # Truth value should be updated
        assert atomspace.atoms[atom1.id].truth_value.strength > 0.5

    def test_get_atom(self):
        atomspace = AtomSpace()
        atom = atomspace.add_atom(AtomType.GOAL, "achieve_goal")
        retrieved = atomspace.get_atom(atom.id)
        assert retrieved is not None
        assert retrieved.id == atom.id
        assert retrieved.name == "achieve_goal"

    def test_find_atoms_by_type(self):
        atomspace = AtomSpace()
        atomspace.add_atom(AtomType.BELIEF, "belief1")
        atomspace.add_atom(AtomType.BELIEF, "belief2")
        atomspace.add_atom(AtomType.GOAL, "goal1")

        beliefs = atomspace.find_atoms(atom_type=AtomType.BELIEF)
        assert len(beliefs) == 2

        goals = atomspace.find_atoms(atom_type=AtomType.GOAL)
        assert len(goals) == 1

    def test_find_atoms_by_strength(self):
        atomspace = AtomSpace()
        atomspace.add_atom(
            AtomType.BELIEF, "weak_belief", TruthValue(strength=0.3, confidence=0.5)
        )
        atomspace.add_atom(
            AtomType.BELIEF, "strong_belief", TruthValue(strength=0.9, confidence=0.8)
        )

        strong_beliefs = atomspace.find_atoms(min_strength=0.7)
        assert len(strong_beliefs) == 1
        assert strong_beliefs[0].name == "strong_belief"

    def test_add_belief(self):
        atomspace = AtomSpace()
        atom = atomspace.add_belief("test belief", strength=0.8, confidence=0.7)
        assert atom.type == AtomType.BELIEF
        assert atom.name == "test belief"
        assert atom.truth_value.strength == 0.8

    def test_add_goal(self):
        atomspace = AtomSpace()
        atom = atomspace.add_goal("complete task", priority=0.9)
        assert atom.type == AtomType.GOAL
        assert atom.metadata["priority"] == 0.9
        assert atom.metadata["status"] == "active"

    def test_add_action(self):
        atomspace = AtomSpace()
        atom = atomspace.add_action("execute_command", success_prob=0.7)
        assert atom.type == AtomType.ACTION
        assert atom.truth_value.strength == 0.7

    def test_link_atoms(self):
        atomspace = AtomSpace()
        atom1 = atomspace.add_atom(AtomType.CONCEPT, "concept1")
        atom2 = atomspace.add_atom(AtomType.CONCEPT, "concept2")

        success = atomspace.link_atoms(atom1.id, atom2.id)
        assert success is True
        assert atom2.id in atomspace.atoms[atom1.id].outgoing
        assert atom1.id in atomspace.atoms[atom2.id].incoming

    def test_get_related_atoms(self):
        atomspace = AtomSpace()
        atom1 = atomspace.add_atom(AtomType.CONCEPT, "concept1")
        atom2 = atomspace.add_atom(AtomType.CONCEPT, "concept2")
        atom3 = atomspace.add_atom(AtomType.CONCEPT, "concept3")

        atomspace.link_atoms(atom1.id, atom2.id)
        atomspace.link_atoms(atom3.id, atom1.id)

        related = atomspace.get_related_atoms(atom1.id)
        assert len(related["outgoing"]) == 1
        assert len(related["incoming"]) == 1

    def test_to_dict(self):
        atomspace = AtomSpace(name="test")
        atomspace.add_belief("test belief")
        atomspace.add_goal("test goal")

        exported = atomspace.to_dict()
        assert exported["name"] == "test"
        assert len(exported["atoms"]) == 2
