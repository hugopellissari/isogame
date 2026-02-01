from unittest.mock import MagicMock

import pytest

from engine.game import Game
from engine.entity import BaseEntity, EntityMap
from engine.terrain import TerrainMap
from engine.system import MovementSystem, InteractionSystem
from engine.trait import MovableTrait, ActorTrait, ReceiverTrait, InteractionVerb
from engine.cqrs import BaseCommand, BaseEvent, CommandHandler, EventHandler

# --- 1. Define Game-Specific Verbs and Logic ---

class MyVerbs(InteractionVerb):
    CHOP = "chop"

class ChopCommand(BaseCommand):
    actor_id: str
    target_id: str

class DamageEvent(BaseEvent):
    target_id: str
    amount: int

# --- 2. Define Handlers ---

class ChopHandler(CommandHandler):
    def __call__(self, game, command: ChopCommand):
        actor = game.entity_map.get(command.actor_id)
        target = game.entity_map.get(command.target_id)
        if actor and target:
            actor.set_action(MyVerbs.CHOP, target.id, target.position)


class DamageHandler(EventHandler):
    def __call__(self, game, event: DamageEvent):
        target = game.entity_map.get(event.target_id)
        # In a real game, you'd find a HealthTrait here
        if not hasattr(target, "hp"):
            target.hp = 100
        target.hp -= event.amount
        if target.hp <= 0:
            game.entity_map.remove(target.id)

# --- 3. Define Concrete Traits ---

class CanChop(ActorTrait):
    range: float = 0
    can_act_on: list = [MyVerbs.CHOP]
    def on_perform_action(self, actor, target):
        return [] # Costs nothing for this test

class Choppable(ReceiverTrait):
    verb: MyVerbs = MyVerbs.CHOP
    def on_receive_action(self, actor, target):
        return [DamageEvent(target_id=target.id, amount=20)]

# --- 4. Define entities ---

class Tree(BaseEntity):
    hp: int = 100


def test_headless_lumberjack_simulation():
    """
    STORY: A lumberjack at (0,0) is told to chop a tree at (5,0).
    It should take several ticks to arrive, and then damage the tree.
    """
    # SETUP
    terrain = MagicMock(spec=TerrainMap) # Terrain isn't used for logic yet
    emap = EntityMap()
    game = Game(terrain, emap)
    
    # Systems
    game.systems.append(MovementSystem())
    game.systems.append(InteractionSystem())
    
    # Handlers
    game.command_processor.register_handler(ChopCommand, ChopHandler())
    game.event_processor.register_handler(DamageEvent, DamageHandler())
    
    # ENTITIES
    lumberjack = BaseEntity(position=(0, 0), traits=[MovableTrait(speed=2.0), CanChop()], asset="lumberjack")
    tree = Tree(position=(5, 0), traits=[Choppable()], asset="tree")
    
    emap.add(lumberjack)
    emap.add(tree)
    
    # ACTION: Issue the Command
    game.enqueue_command(ChopCommand(actor_id=lumberjack.id, target_id=tree.id))
    
    # TICK 1: Process Command
    # The handler will set the destination and target_id
    game.tick(0.1) 
    assert lumberjack.is_moving is True
    assert lumberjack.destination == (5, 0)
    
    # TICK 2-24: Travel time
    # At speed 2.0 and dt 0.1, it covers 0.2 units per tick.
    # It needs to travel 5 units, so ~25 ticks to arrive.
    for _ in range(25):
        game.tick(0.1)
    
    # CHECK POSITION (Should be at or very near the tree)
    # This must be the position of the lumberjack - the range, as it gets just as close
    # as it needs to trigger the inrteraction
    assert lumberjack.position == pytest.approx((5, 0))
    assert lumberjack.is_moving is False
    
    # TICK 26: The Handshake
    # Now in range, the InteractionSystem should trigger the DamageEvent
    game.tick(0.1)
    
    # VERIFY REALITY
    # This is currenetly failing because there is no cooldown in the actions,
    # so it performs like crazy! It should wait X ticks before performing again
    assert tree.hp == 80 # 100 - 20 damage
    print(f"Simulation Success: Tree HP is {tree.hp}")

    # TICK 27-30: Continued Chopping
    for _ in range(4):
        game.tick(0.1)
    
    # Tree should be gone (100 - (5 * 20) = 0)
    assert emap.get(tree.id) is None
    print("Simulation Success: Tree has been fully processed and removed.")
