from engine.core.cqrs import BaseEvent


class EntityArrivedEvent(BaseEvent):
    entity_id: str
