# import random
from datetime import datetime

from persistqueue import SQLiteAckQueue

# import globals
import hassapi as hass
import mqttapi as mqtt


class Notifications(hass.Hass):
    def initialize(self):
        self.qPath = "notification_q"
        self.types = self.args["types"]
        self.defaults = self.args["default_destinations"]
        self.tts = self.get_app("sound")
        self.qSizeLocation = "input_number.queue_size"
        self.someoneHomeLocation = self.entities.input_boolean.someone_home.state

        self.listen_state(self.get_notifications, "binary_sensor.someone_home")

    # ----------- Helper functions -----------

    # self.turn_on("entity.name")

    def someone_home(self):
        return self.someoneHomeLocation

    # ----------- Main functions -----------

    def new_notification(self, notificationType, message):
        """Raise a new notification with a given 'type' and 'message'"""
        urgency = self.types[notificationType]["urgency"]
        destination = self.types[notificationType].get(
            "destination", self.defaults[urgency]
        )

        notifications = 0

        if self.someone_home():
            if urgency in ("Immediate", "Both", "Queued", "If_Home"):
                self.send_notification(message, destination, title=notificationType)
                notifications += 1
        else:
            if urgency in ("Immediate", "Both"):
                self.send_notification(message, destination, title=notificationType)
                notifications += 1
            if urgency in ("Queued", "Both"):
                # Store notification in queue for later
                self.queue_notification(message, destination, notificationType)
                notifications += 1

        if notifications == 0:
            self.log(f"'{urgency}' is not a valid urgency.", level="ERROR")

    def send_notification(
        self, message, destination, notificationType, title="", time=""
    ):
        if destination.split(".")[0] == "media_player":
            try:
                self.tts.notify(
                    message,
                    notificationType,
                    destination,
                    time,
                )
            except:
                self.log(f"Error sending notification.", level="ERROR")
                return False
        else:
            try:
                self.notify(message, title=title, name=destination)
            except:
                self.log(f"Error sending notification.", level="ERROR")
                return False
        return True

    def queue_notification(self, message, destination, notificationType):
        q = SQLiteAckQueue(self.qPath)
        q.put(
            {
                "message": message,
                "destination": destination,
                "notificationType": notificationType,
                "time": datetime.now(),
            }
        )
        # Update helper to show number of notifications waiting. active_size includes ack cache
        self.set_value(self.qSizeLocation, self.q.active_size())

    def get_notifications(self, entity, attribute, old, new, kwargs):
        if new == False:  # Only continue if someone is home
            return
        q = SQLiteAckQueue(self.qPath)

        # Make list of speech notes and publish together
        voiceNotes = []
        while q.qsize > 0:  # qSize reduces with get()
            notification = q.get()

            if notification["time"].day == datetime.today().day:
                # Time only
                title = (
                    notification["notificationType"]
                    + "from "
                    + notification["time"].time()
                )
            else:  # Include date
                title = (
                    notification["notificationType"] + "from " + notification["time"]
                )

            if notification["destination"].split(".")[0] == "media_player":
                voiceNotes.append(notification)
            # Others are sent individually
            elif self.send_notification(
                notification["message"],
                notification["destination"],
                notification["notificationType"],
                title,
                notification["time"],
            ):
                self.q.ack(notification)
            else:
                self.q.nack(notification)
                self.log(f"Notifications not delivered", level="ERROR")

        if self.tts.multi_notify(voiceNotes):
            [q.ack(item) for item in voiceNotes]
        else:
            [q.nack(item) for item in voiceNotes]
            self.log(f"Notifications not delivered", level="ERROR")


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
