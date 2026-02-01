from pydantic import BaseModel


class BaseEvent(BaseModel):
    pass


class BaseCommand(BaseModel):
    pass


class CommandHandler:
    def process(self, game, command: BaseCommand):
        """Logic to validate intent and update entity state flags."""
        raise NotImplementedError


class EventHandler:
    def process(self, game, event: BaseEvent):
        """Logic to apply a final change to the world state."""
        raise NotImplementedError


class CommandProcessor:
    def __init__(self):
        self._handlers: dict[type[BaseCommand], CommandHandler] = {}

    def register_handler(self, command_type: type[BaseCommand], handler: CommandHandler):
        self._handlers[command_type] = handler

    def process(self, game, command_queue: list[BaseCommand]):
        # We work on a copy so we can clear the original queue
        for cmd in command_queue:
            handler = self._handlers.get(type(cmd))
            if handler:
                handler.process(game, cmd)
            else:
                print(f"Warning: No handler registered for {type(cmd).__name__}")


class EventProcessor:
    def __init__(self):
        # A dictionary mapping Event Types to a LIST of Handlers
        self._handlers: dict[type[BaseEvent], list[EventHandler]] = {}

    def register_handler(self, event_type: type[BaseEvent], handler: EventHandler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def process(self, game, event_queue: list[BaseEvent]):
        for event in event_queue:
            handlers = self._handlers.get(type(event), [])
            for handler in handlers:
                handler.process(game, event)
