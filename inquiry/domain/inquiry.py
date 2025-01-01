from dataclasses import dataclass
from datetime import datetime


@dataclass
class Inquiry:
    id: str
    name: str
    email: str
    content: str
    is_replied: bool
    created_at: datetime
