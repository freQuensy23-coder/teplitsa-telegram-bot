import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Notification:
    title: str
    message: str
    time: datetime
    important_level: int


class SimpleNotificationSender:
    def __init__(self):
        self.notifications = []

    def add_notification(self, notification):
        self.notifications.append(notification)

    def get_notification(self):
        return self.notifications
