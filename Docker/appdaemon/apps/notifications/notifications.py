import random
import time

from persistqueue import Queue

import globals
import hassapi as hass
import mqttapi as mqtt


class Notifications(hass.Hass):
    def initialize(self):
        # Initialize callbacks
        self.q = Queue("mypath")

    def new_notification_mqtt(self, event_name, data, kwargs):
        """Raise a new notification from an MQTT message"""
        self.log("{} - {} - {} ".format(event_name, data, kwargs), level="DEBUG")

    def new_notification(self, type, message):
        """Raise a new notification with a given 'type' and 'message'"""
        urgency = self.check_urgency(type)
        if urgency == "Immediate":
            self.notify_urgent(message)
        if urgency == "Queued":
            self.notify_not_urgent(message)

    def check_urgency(self, type):
        """Check whether nofication can be queued"""
        return self.urgencies[type]

    def notify_later(self):
        self.q.put("a")
        self.q.get()
        self.q.task_done()  # Remove from q


class NotificationListener(mqtt.Mqtt):
    def initialize(self):
        self.notifications = Notifications
        self.listen_event(
            self.notifications.new_notification_mqtt,
            "MQTT_MESSAGE",
            wildcard="homeassistant/notifications/#",
        )
