import dataclasses
from abc import ABC
from datetime import datetime, timedelta
import gspread
import config

sa = gspread.service_account(filename="google_key.json")
sh = sa.open("TeplNotifyBot")
wks = sh.get_worksheet(0)


@dataclasses.dataclass
class Notification:
    title: str
    notify_time = timedelta(minutes=45)
    message: str
    time: datetime
    important_level: int
    notified: bool
    notified = False

    def __str__(self):
        return f"*{self.title}*\n{self.message}"

    def __repr__(self):
        return f"Notification(title='{self.title}', message='{self.message}', time='{self.time}', important_level='{self.important_level}')"

    def __eq__(self, other):
        if isinstance(other, Notification):
            return self.title == other.title and self.message == other.message and self.time == other.time and self.important_level == other.important_level
        if isinstance(other, list):
            return self.title == other[0] and self.message == other[1] and \
                   self.time == datetime.strptime(other[2], "%d.%m.%Y %H:%M") and\
                   self.important_level == int(other[3])


class AbstractNotificationController:
    def set_notified(self, notification: Notification):
        raise NotImplementedError()

    def get_notifications(self):
        raise NotImplementedError()

    def current_notifications(self):
        for notification in self.get_notifications():
            if notification.time - datetime.now() < notification.notify_time and not notification.notified:
                yield notification
                notification.notified = True
                self.set_notified(notification)


class MemoryNotificationController:
    def __init__(self):
        self._notifications = []

    def add_notification(self, notification):
        self._notifications.append(notification)

    def get_notifications(self):
        return self._notifications

    def set_notified(self, notification):
        notification.notified = True
        self._notifications.remove(notification)


class GoogleSheetsNotificationController(AbstractNotificationController):
    def __init__(self, api_key_fname=config.GOOGLE_API_FILE_NAME, sheet_name=config.GOOGLE_SHEET_NAME):
        sa = gspread.service_account(filename=api_key_fname)
        sheet = sa.open(sheet_name)
        self.wks = sheet.get_worksheet(0)

    def get_notifications_as_list(self):
        return self.wks.get("A2:F200")

    def get_notifications(self):
        notifications = self.get_notifications_as_list()
        for i, notification_as_list in enumerate(notifications):
            yield Notification(title=notification_as_list[0], message=notification_as_list[1],
                               time=datetime.strptime(notification_as_list[2], "%d.%m.%Y %H:%M"),
                               important_level=int(notification_as_list[3]), notified=notification_as_list[5] == "1")

    def set_notified(self, notification_to_set):
        notifications = self.get_notifications_as_list()
        for i, notification_as_list in enumerate(notifications):
            if notification_to_set == notification_as_list:
                notifications[i][5] = "1"
                self.wks.update_cell(i + 2, 6, "1")
                notification_to_set.notified = True
                return True
        raise ValueError("Notification not found")
