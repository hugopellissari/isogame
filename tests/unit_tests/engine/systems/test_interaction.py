from typing import ClassVar
from unittest.mock import MagicMock
from engine.core.entity import BaseEntity, EntityMap
from engine.core.game import Game
from engine.core.cqrs import BaseEvent
from engine.core.system import InteractionSystem
from engine.core.trait import ActorTrait, ReceiverTrait, InteractionVerb


class Verb(InteractionVerb):
    CHOP = "chop"


# Concrete traits for testing
class CanChop(ActorTrait):
    range: float = 2.0
    verb: ClassVar[Verb] = Verb.CHOP


class Choppable(ReceiverTrait):
    verb: ClassVar[Verb] = Verb.CHOP


class ChopSystem(InteractionSystem):
    @property
    def actor_trait_subclass(self) -> type[ActorTrait]:
        return CanChop

    def handle_action(self, actor: BaseEntity, target: BaseEntity) -> list[BaseEvent]:
        return ["some event", "another event"]


def test_interaction_handshake_in_range():
    system = ChopSystem()
    emap = EntityMap()
    game = Game(MagicMock(), emap)

    # Standardize Verb: Use Verb.CHOP consistently
    actor = BaseEntity(position=(0, 0), traits=[CanChop(range=2.0)], asset="lumberjack")
    actor.get_trait(CanChop).activate("tree_1")

    target = BaseEntity(
        id="tree_1", position=(1, 0), traits=[Choppable()], asset="tree"
    )

    emap.add(actor)
    emap.add(target)

    system.update(game, 0.1)
    assert len(game.event_queue) == 2


def test_interaction_out_of_range():
    """Verify no interaction occurs if the target is too far."""
    system = InteractionSystem()
    game = MagicMock()

    actor = BaseEntity(position=(0, 0), traits=[CanChop()], asset="lumberjack")
    actor.get_trait(CanChop).activate("tree_1")

    target = BaseEntity(position=(10, 0), asset="tree")  # Way out of range
    target.traits = [Choppable()]

    game.entities.get.return_value = target
    game.entities.entities = {"lumberjack": actor}

    system.update(game, 0.1)

    game.enqueue_event.assert_not_called()


def test_interaction_target_missing_clears_action():
    system = InteractionSystem()
    game = MagicMock()  # Still using mock here, so we must prime it

    actor = BaseEntity(position=(0, 0), traits=[CanChop()], asset="lumberjack")
    actor.get_trait(CanChop).activate("tree_1")

    # PRIME THE MOCK: Tell it to return our actor in the loop
    game.entities.get_active_entities.return_value = [actor]
    game.entities.get.return_value = None

    system.update(game, 0.1)
