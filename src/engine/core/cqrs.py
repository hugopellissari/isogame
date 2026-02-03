from pydantic import BaseModel


class BaseEvent(BaseModel):
    """
    An immutable representation of a fact that has already occurred in the game world.
    Events are the results of system logic and are used to apply final state changes.
    """

    pass



class BaseCommand(BaseModel):
    """
    A request to change the game state or initiate an action.
    Commands represent player or AI intent and are subject to validation by handlers.
    """

    pass


class CommandHandler:
    """
    Interface for logic that validates a specific Command.
    If valid, the handler updates entity 'intent' flags (e.g., target_id, is_active).
    """

    def __call__(self, game, command: BaseCommand):
        """
        Validates the command against game rules and updates entity state.

        Args:
            game: The central Game instance.
            command: The specific BaseCommand being processed.
        """
        raise NotImplementedError


class EventHandler:
    """
    Interface for logic that reacts to a specific Event.
    Handlers here apply 'The Hand of God'—mutating raw data like health or inventory.
    """

    def __call__(self, game, event: BaseEvent):
        """
        Executes the final mutation of the game world based on a confirmed event.

        Args:
            game: The central Game instance.
            event: The specific BaseEvent being processed.
        """
        raise NotImplementedError


class CommandProcessor:
    """
    Routes incoming Commands to their registered Handlers.
    Each Command type maps to exactly one Handler to ensure deterministic validation.
    """

    def __init__(self):
        self._handlers: dict[type[BaseCommand], CommandHandler] = {}

    def register_handler(
        self, command_type: type[BaseCommand], handler: CommandHandler
    ):
        """Registers a singleton handler for a specific command type."""
        self._handlers[command_type] = handler

    def process(self, game, command_queue: list[BaseCommand]):
        """Iterates through the queue and executes handlers for registered commands."""
        for cmd in command_queue:
            handler = self._handlers.get(type(cmd))
            if handler:
                handler(game, cmd)
            else:
                print(f"Warning: No handler registered for {type(cmd).__name__}")


class EventProcessor:
    """
    Routes occurring Events to all interested Handlers.
    Supports multiple handlers per event, allowing decoupled reactions
    (e.g., one handler updates health, another plays a sound).
    """

    def __init__(self):
        self._handlers: dict[type[BaseEvent], list[EventHandler]] = {}

    def register_handler(self, event_type: type[BaseEvent], handler: EventHandler):
        """Subscribes a handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def process(self, game, event_queue: list[BaseEvent]):
        """Dispatches every event in the queue to all subscribed handlers."""
        for event in event_queue:
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                handler(game, event)
