from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any
from uuid import UUID

class EventBase(BaseModel):
    event_id: str
    timestamp: datetime
    source: str
    topic: str
    payload: Dict[str, Any]
    snapshot: Dict[str, Any]

class UserRegistrationEvent(EventBase):
    pass

class WelcomeEvent(EventBase):
    pass