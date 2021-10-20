from datetime import datetime

import hassapi as hass


class Sound(hass.Hass):
    def initialize(self):
        pass

    def notify(self, message, notificationType, destination, time):
        """"""
        #  self.call_service("tts/google_translate_say", entity_id = current_speaker, message = data["text"])
        pass

    def multi_notify(self, notifications):
        """"""
        pass
