# from datetime import datetime

import hassapi as hass


class Sound(hass.Hass):
    def initialize(self):
        self.home = self.get_app("home")
        
        self.speakerSwitch = self.args["speaker_switch"]
        self.speakerDevice = self.args["speaker_device"]
        self.speakerPowerSwitch = self.args["speaker_power_switch"]
        self.speakerVol = self.args["speaker_vol"]
        self.deviceVol = self.args["device_vol"]
        onTime = self.args["on_time"]
        offTime = self.args["off_time"]

        self.run_daily(self.speaker_power, onTime, state="on")
        self.run_daily(self.speaker_power, offTime, state="off")
        self.listen_state(self._someone_home, self.home.get_home_boolean())
        self.listen_state(self.speaker_switch_1, self.speakerSwitch)

    def _someone_home(self, entity, attribute, old, new, kwargs):
        if new != "on":
            self.speaker_power() # Turn off speaker if noone home

    def speaker_power(self, kwargs=""):
        # Defaults to turning off 
        if not self.home.is_home():
            self.log(f"User not home. Speaker power set to off.", level="INFO")
            self.turn_off(self.speakerSwitch)
            return
        self.turn_on(self.speakerSwitch) if kwargs["state"] == "on" else self.turn_off(self.speakerSwitch)
        self.log(f"Speaker set to {kwargs['state']}", level="INFO")

    def speaker_switch_1(self, entity, attribute, old, new, kwargs):
        t = 90 if new == "on" else 1
        self.handle = self.run_in(self.speaker_switch_2, t, on=new)

    def speaker_switch_2(self, kwargs):
        if kwargs["new"] == "on":
            self.turn_on(self.speakerPowerSwitch)
            vol = self.speakerVol
        else:
            self.turn_off(self.speakerPowerSwitch)
            vol = self.deviceVol
        self.call_service("media_player/volume_set", entity_id = self.speakerDevice, volume_level = vol)
        self.log(f"Speaker vol set to {vol}", level="INFO")

    def notify(self, message, notificationType, destination, time):
        """"""
        #  self.call_service("tts/google_translate_say", entity_id = current_speaker, message = data["text"])
        pass

    def multi_notify(self, notifications):
        """"""
        pass
