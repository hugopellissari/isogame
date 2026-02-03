from unittest.mock import MagicMock

from engine.core.cqrs import (
    CommandHandler,
    CommandProcessor,
    EventHandler,
    BaseCommand,
    BaseEvent,
    EventProcessor,
)


# 1. Define Test Concrete Classes
class ChopCommand(BaseCommand):
    target_id: str


class DamageEvent(BaseEvent):
    amount: int


class ChopHandler(CommandHandler):
    def __call__(self, game, command: ChopCommand):
        # Logic: Immediately assume valid for test
        game.logic_flag = "checked"


class DamageHandler(EventHandler):
    def __call__(self, game, event: DamageEvent):
        game.health_result -= event.amount


# 2. The Tests


def test_command_to_handler_execution():
    """Verify that the CommandProcessor triggers the right logic."""
    proc = CommandProcessor()
    proc.register_handler(ChopCommand, ChopHandler())

    # Mock world state
    mock_game = MagicMock()
    mock_game.logic_flag = "none"

    cmd = ChopCommand(target_id="tree_1")
    proc.process(mock_game, [cmd])

    assert mock_game.logic_flag == "checked"


def test_event_multi_subscription():
    """Verify that multiple handlers can react to one event."""
    proc = EventProcessor()
    mock_game = MagicMock()
    mock_game.health_result = 100

    # Register two damage handlers
    proc.register_handler(DamageEvent, DamageHandler())
    proc.register_handler(DamageEvent, DamageHandler())

    event = DamageEvent(amount=10)
    proc.process(mock_game, [event])

    # If both ran, 100 - 10 - 10 = 80
    assert mock_game.health_result == 80


def test_unregistered_command_graceful_fail():
    """Ensure the system doesn't crash if a command has no handler."""
    proc = CommandProcessor()
    mock_game = MagicMock()

    class UnknownCommand(BaseCommand):
        pass

    # This should just pass silently or log
    proc.process(mock_game, [UnknownCommand()])
