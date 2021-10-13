import random
import time

from persistqueue import Queue

# import globals
import hassapi as hass
import mqttapi as mqtt


class Notifications(hass.Hass):
    def initialize(self):
        # Initialize callbacks
        self.q = Queue("mypath")

    def new_notification(self, type, message):
        """Raise a new notification with a given 'type' and 'message'"""
        urgency = self.check_urgency(type)
        notifications = 0
        if urgency in ("Immediate", "Both"):
            self.notify_urgent(message)
            notifications += 1
        if urgency in ("Queued", "Both"):
            self.notify_not_urgent(message, urgency)
            notifications += 1
        if notifications == 0:
            self.log(f"'{urgency}' is not a valid urgency.", level="ERROR")

    def check_urgency(self, type):
        """Check whether nofication can be queued"""
        return self.urgencies[type]

    def notify_not_urgent(self, message, urgency):
        """Check if home"""
        self.notify_later(message, urgency)

    def notify_later(self):
        self.q.put("a")
        self.q.get()
        self.q.task_done()  # Remove from q


class NotificationListener(mqtt.Mqtt):
    def initialize(self):
        self.notifications = self.get_app("notifications")
        # Get config for notifications. For each note type, do following:
        self.listen_event(
            self.receive_notification,
            "MQTT_MESSAGE",
            namespace="mqtt",
            topic="homeassistant/notifications/danger",
        )

    def receive_notification(self, event_name, data, kwargs):
        notificationType = data["topic"].replace("homeassistant/notifications/", "")
        message = data["payload"]
        self.log(
            f"MQTT notification received. Payload: '{message}'. Topic: '{data['topic']}'. Type: '{notificationType}'",
            level="DEBUG",
        )
        self.notifications.new_notification(notificationType, message)
