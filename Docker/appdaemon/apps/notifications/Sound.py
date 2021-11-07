# from datetime import datetime

import hassapi as hass


class Sound(hass.Hass):
    def initialize(self):
        self.home = self.get_app("home")
        
        self.log(f"Testing logger", level="INFO")

        self.speakerSwitch = self.args["speaker_switch"]
        self.speakerDevice = self.args["speaker_device"]
        self.speakerVol = self.args["speaker_vol"]
        self.deviceVol = self.args["device_vol"]

        self.run_daily(self.speaker_power, "09:30:00", state="on")
        self.run_daily(self.speaker_power, "21:00:00", state="off")
        self.listen_state(self.speaker_power, self.home.get_home_boolean(), new="off")
        self.listen_state(self.speaker_switch_vol, self.speakerSwitch)

    def speaker_power(self, entity="", attribute="", old="", new="", kwargs=""):
        # Defaults to turning off 
        if not self.home.is_home():
            self.log(f"User not home. Speaker power set to off.", level="INFO")
            self.turn_off(self.speakerSwitch)
            return
        self.turn_on(self.speakerSwitch) if kwargs["state"] == "on" else self.turn_off(self.speakerSwitch)

    def speaker_switch_vol(self, entity, attribute, old, new, kwargs):
        if old == "off" and new == "on":
            vol = self.speakerVol
        elif old == "on" and new == "off":
            vol = self.deviceVol
        self.call_service("media_player/volume_set", entity_id = self.speaker, volume_level = vol)

    def notify(self, message, notificationType, destination, time):
        """"""
        #  self.call_service("tts/google_translate_say", entity_id = current_speaker, message = data["text"])
        pass

    def multi_notify(self, notifications):
        """"""
        pass
