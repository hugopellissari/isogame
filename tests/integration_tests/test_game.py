from typing import ClassVar
from unittest.mock import MagicMock

import pytest

from engine.core.game import Game
from engine.core.entity import BaseEntity, EntityMap
from engine.core.terrain import TerrainMap
from engine.core.system import MovementSystem, InteractionSystem
from engine.core.trait import MovableTrait, ActorTrait, ReceiverTrait, InteractionVerb
from engine.core.cqrs import BaseCommand, BaseEvent, CommandHandler, EventHandler


class MyVerbs(InteractionVerb):
    CHOP = "chop"


class ChopCommand(BaseCommand):
    actor_id: str
    target_id: str


class ChopReceivedEvent(BaseEvent):
    target_id: str
    amount: int


class ChopperTrait(ActorTrait):
    range: float = 0
    damage: int = 20
    verb: ClassVar[InteractionVerb] = MyVerbs.CHOP


class Choppable(ReceiverTrait):
    verb: MyVerbs = MyVerbs.CHOP
    hp: int


class ChopHandler(CommandHandler):
    def __call__(self, game, command: ChopCommand):
        actor = game.entities.get(command.actor_id)
        target = game.entities.get(command.target_id)
        if actor and target:
            chop_trait = actor.get_trait(ChopperTrait)
            chop_trait.activate(target.id)


class ChoppingHandler(EventHandler):
    def __call__(self, game, event: ChopReceivedEvent):
        target = game.entities.get(event.target_id)
        trait = target.get_trait(Choppable)
        trait.hp -= event.amount
        if trait.hp <= 0:
            game.entities.remove(target.id)


class ChoppingSystem(InteractionSystem):
    @property
    def actor_trait_subclass(self) -> type[ActorTrait]:
        return ChopperTrait

    def handle_action(self, actor: BaseEntity, target: BaseEntity) -> list[BaseEvent]:
        chop_trait = actor.get_trait(ChopperTrait)
        if not chop_trait:
            return []
        damage = chop_trait.damage
        return [ChopReceivedEvent(target_id=target.id, amount=damage)]


def test_headless_lumberjack_simulation():
    """
    STORY: A lumberjack at (0,0) is told to chop a tree at (5,0).
    It should take several ticks to arrive, and then damage the tree.
    """
    # SETUP
    terrain = MagicMock(spec=TerrainMap)  # Terrain isn't used for logic yet
    emap = EntityMap()
    game = Game(terrain, emap)

    # Systems
    game.systems.append(MovementSystem())
    game.systems.append(ChoppingSystem())

    # Handlers
    game.command_processor.register_handler(ChopCommand, ChopHandler())
    game.event_processor.register_handler(ChopReceivedEvent, ChoppingHandler())

    # ENTITIES
    lumberjack = BaseEntity(
        position=(0, 0),
        traits=[MovableTrait(speed=2.0), ChopperTrait()],
        asset="lumberjack",
    )
    tree = BaseEntity(position=(5, 0), traits=[Choppable(hp=100)], asset="tree")

    emap.add(lumberjack)
    emap.add(tree)

    # ACTION: Issue the Command
    game.enqueue_command(ChopCommand(actor_id=lumberjack.id, target_id=tree.id))

    # TICK 1: Process Command
    # The handler will set the destination and target_id
    game.tick(0.1)
    assert lumberjack.get_trait(MovableTrait).is_moving is True
    assert lumberjack.get_trait(MovableTrait).destination == (5, 0)

    # TICK 2-24: Travel time
    # At speed 2.0 and dt 0.1, it covers 0.2 units per tick.
    # It needs to travel 5 units, so ~25 ticks to arrive.
    for _ in range(25):
        game.tick(0.1)

    # CHECK POSITION (Should be at or very near the tree)
    # This must be the position of the lumberjack - the range, as it gets just as close
    # as it needs to trigger the inrteraction
    assert lumberjack.position == pytest.approx((5, 0))
    assert lumberjack.get_trait(MovableTrait).is_moving is False

    # TICK 26: The Handshake
    # Now in range, the InteractionSystem should trigger the DamageEvent
    game.tick(0.1)

    # VERIFY REALITY
    # This is currenetly failing because there is no cooldown in the actions,
    # so it performs like crazy! It should wait X ticks before performing again
    assert tree.get_trait(Choppable).hp == 80  # 100 - 20 damage
    print(f"Simulation Success: Tree HP is {tree.get_trait(Choppable).hp}")

    # TICK 27-30: Continued Chopping
    for _ in range(4):
        game.tick(0.1)

    # Tree should be gone (100 - (5 * 20) = 0)
    assert emap.get(tree.id) is None
    print("Simulation Success: Tree has been fully processed and removed.")
