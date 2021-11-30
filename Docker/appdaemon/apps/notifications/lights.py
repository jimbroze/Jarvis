# from datetime import datetime

import hassapi as hass


class Lights(hass.Hass):
    def initialize(self):
        self.home = self.get_app("home")
        
        self.allLights = self.args["all_lights"] # TODO change to auto array of all lights minus specifics
        self.bedroomLights = self.args["bedroom_light"]
        wakeupTime = self.args["wakeup_time"]
        # offTime = self.args["off_time"]
        
        self.run_daily(self.wakeup_lights, wakeupTime)
        # self.run_daily(self.speaker_power, offTime, state="off")
        self.listen_state(self._someone_home, self.home.get_home_boolean())
        self.listen_state(self._sun_lights, "sun.sun", attribute="elevation")

    def _elevation_threshold(self):
        return 4 if self.get_state("weather.jarvis") == "sunny" else 8

    def _someone_home(self, entity, attribute, old, new, kwargs):
        if not self.home.is_home():
            self.turn_off(self.allLights)
            self.log(f"User not home. Lights turned off.", level="INFO")
            return

        if self.get_state("light.living_room_light") == "off":
            if self.get_state("sun.sun", "elevation") < self._elevation_threshold():
                self.turn_on("light.living_room_light")
        elif self.get_state("light.living_room_light") == "on":
            if self.get_state("sun.sun", "elevation") > self._elevation_threshold():
                self.turn_off("light.living_room_light")

    def _sun_lights(self, entity, attribute, old, new, kwargs):
        if not self.home.is_home():
            return
        elevationThreshold = self._elevation_threshold()
        if old < elevationThreshold and new > elevationThreshold:
                self.turn_off("light.living_room_light")
        elif old > elevationThreshold and new < elevationThreshold:
                self.turn_on("light.living_room_light")


        
    def wakeup_lights(self, kwargs):
        # Defaults to turning off 
        if not self.home.is_home():
            self.log(f"User not home. Lights left off.", level="INFO")
            return
        self.turn_on(self.bedroomLights)
        self.log(f"Turning on morning lights.", level="INFO")


    # def speaker_switch_vol(self, entity, attribute, old, new, kwargs):
    #     if old == "off" and new == "on":
    #         vol = self.speakerVol
    #     elif old == "on" and new == "off":
    #         vol = self.deviceVol
    #     self.call_service("media_player/volume_set", entity_id = self.speaker, volume_level = vol)
    #     self.log(f"Speaker vol set to {vol}", level="INFO")