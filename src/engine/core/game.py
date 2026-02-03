from abc import abstractmethod

from engine.core.entity import EntityMap
from engine.core.cqrs import BaseCommand, BaseEvent, EventProcessor, CommandProcessor
from engine.core.system import System
from engine.core.terrain import TerrainMap


class Game:
    """
    The central hub of the engine.core. It manages the lifecycle of
    entities, systems, commands, and events.
    """

    def __init__(self, terrain: TerrainMap, entities: EntityMap, systems: list[System]):
        self.terrain = terrain
        self.entities = entities

        # Simulation components
        self.systems = systems

        # Transaction Queues
        self.command_queue: list["BaseCommand"] = []
        self.event_queue: list["BaseEvent"] = []

        # Processors
        self.command_processor = CommandProcessor()
        self.event_processor = EventProcessor()

    def enqueue_command(self, command: "BaseCommand"):
        self.command_queue.append(command)

    def enqueue_event(self, event: "BaseEvent"):
        self.event_queue.append(event)

    def tick(self, dt: float):
        """
        The deterministic heartbeat of the game.
        """
        # 1. Intent: What does the user/AI want to do?
        self.command_processor.process(self, self.command_queue)
        self.command_queue.clear()

        # 2. Simulation: Passage of time and logic checks
        for system in self.systems:
            system.update(self, dt)

        # 3. Reality: Apply the results of the simulation
        self.event_processor.process(self, self.event_queue)
        self.event_queue.clear()
