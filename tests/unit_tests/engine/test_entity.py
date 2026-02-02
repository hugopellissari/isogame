import pytest
from unittest.mock import MagicMock
from engine.entity import BaseEntity, EntityMap
from engine.trait import ActorTrait, BaseTrait, InteractionVerb, MovableTrait

# --- Mock Implementation for Testing ---

class MockVerbs(InteractionVerb):
    CHOP = "chop"
    EAT = "eat"

class MockChopTrait(ActorTrait):
    can_act_on: list = [MockVerbs.CHOP]
    range: float = 1.5

# --- Tests ---

def test_implement_me():
    assert False, "implememt those tests"