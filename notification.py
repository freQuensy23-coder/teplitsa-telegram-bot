import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Notification:
    title: str
    message: str
    time: datetime
    important_level: int