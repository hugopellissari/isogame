import pytest
from engine.core.cqrs import (
    BaseCommand, 
    BaseEvent, 
    CommandProcessor, 
    EventProcessor
)

# --- Mocks ---

class MockGame:
    """A dummy game object to pass to handlers."""
    pass

class MoveCommand(BaseCommand):
    x: int
    y: int

class AttackCommand(BaseCommand):
    target_id: str

class EntityMovedEvent(BaseEvent):
    entity_id: str
    new_pos: tuple[int, int]

class ScoreChangedEvent(BaseEvent):
    score: int

# --- Fixtures ---

@pytest.fixture
def mock_game():
    return MockGame()

@pytest.fixture
def command_processor():
    return CommandProcessor()

@pytest.fixture
def event_processor():
    return EventProcessor()

# --- Command Processor Tests ---

def test_command_registration_and_execution(command_processor, mock_game):
    """Test that a registered handler receives the command."""
    
    # Capture state to verify execution
    execution_log = []

    def handle_move(game, command: MoveCommand):
        execution_log.append(command)

    # Register
    command_processor.register_handler(MoveCommand, handle_move)
    
    # Process
    cmd = MoveCommand(x=10, y=20)
    command_processor.process(mock_game, [cmd])

    assert len(execution_log) == 1
    assert execution_log[0].x == 10
    assert execution_log[0].y == 20

def test_command_unregistered_warning(command_processor, mock_game, capsys):
    """Test that processing an unknown command is safe (no crash) and warns."""
    
    # Don't register anything
    cmd = AttackCommand(target_id="enemy_1")
    command_processor.process(mock_game, [cmd])

    # Check stdout for the warning message
    captured = capsys.readouterr()
    assert "Warning: No handler registered for AttackCommand" in captured.out

def test_command_queue_processing(command_processor, mock_game):
    """Test processing multiple commands in a single tick."""
    
    execution_count = 0
    def handle_move(game, cmd):
        nonlocal execution_count
        execution_count += 1
        
    command_processor.register_handler(MoveCommand, handle_move)
    
    # Queue with 3 commands
    queue = [
        MoveCommand(x=1, y=1),
        MoveCommand(x=2, y=2),
        MoveCommand(x=3, y=3)
    ]
    
    command_processor.process(mock_game, queue)
    assert execution_count == 3

# --- Event Processor Tests ---

def test_event_single_subscriber(event_processor, mock_game):
    """Test basic event listening."""
    triggered = False
    
    def on_moved(game, event: EntityMovedEvent):
        nonlocal triggered
        triggered = True

    event_processor.register_handler(EntityMovedEvent, on_moved)
    
    event = EntityMovedEvent(entity_id="p1", new_pos=(10, 10))
    event_processor.process(mock_game, [event])
    
    assert triggered is True

def test_event_multiple_subscribers(event_processor, mock_game):
    """
    Test 1-to-Many broadcasting. 
    One event should trigger multiple independent handlers.
    """
    results = []

    def log_analytics(game, event):
        results.append("analytics")

    def play_sound(game, event):
        results.append("sound")

    # Register both for the same event type
    event_processor.register_handler(EntityMovedEvent, log_analytics)
    event_processor.register_handler(EntityMovedEvent, play_sound)

    event = EntityMovedEvent(entity_id="p1", new_pos=(5, 5))
    event_processor.process(mock_game, [event])

    assert len(results) == 2
    assert "analytics" in results
    assert "sound" in results

def test_event_no_subscribers_is_safe(event_processor, mock_game):
    """Test that events with no listeners disappear silently (no error)."""
    event = ScoreChangedEvent(score=100)
    
    # Should not raise exception
    event_processor.process(mock_game, [event]) 

def test_event_mixed_queue(event_processor, mock_game):
    """Test that the processor correctly routes different events to different handlers."""
    moved_count = 0
    score_count = 0

    event_processor.register_handler(EntityMovedEvent, lambda g, e: locals().update(moved_count=moved_count + 1)) # Lambda hack won't work for closure var assignment usually, let's use standard functions
    
    def on_moved(g, e): nonlocal moved_count; moved_count += 1
    def on_score(g, e): nonlocal score_count; score_count += 1

    event_processor.register_handler(EntityMovedEvent, on_moved)
    event_processor.register_handler(ScoreChangedEvent, on_score)

    queue = [
        EntityMovedEvent(entity_id="a", new_pos=(0,0)),
        ScoreChangedEvent(score=10),
        EntityMovedEvent(entity_id="b", new_pos=(1,1))
    ]

    event_processor.process(mock_game, queue)

    assert moved_count == 2
    assert score_count == 1