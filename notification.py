import dataclasses
from datetime import datetime, timedelta


@dataclasses.dataclass
class Notification:
    title: str
    notify_time = timedelta(minutes=45)
    message: str
    time: datetime
    important_level: int
    notified = False

    def __str__(self):
        return f"*{self.title}*\n{self.message}"


class SimpleNotificationSender:
    def __init__(self):
        self._notifications = []

    def add_notification(self, notification):
        self._notifications.append(notification)

    def get_notification(self):
        return self._notifications

    def current_notifications(self):
        for notification in self._notifications:
            if notification.time - datetime.now() < notification.notify_time and not notification.notified:
                yield notification
                notification.notified = True
                self._notifications.remove(notification)
