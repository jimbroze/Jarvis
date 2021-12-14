# from datetime import datetime
import re

import hassapi as hass
import mqttapi as mqtt


class Lights(hass.Hass):
    def initialize(self):
        self.home = self.get_app("home")
        self.lightListener = self.get_app("light_listener")
        
        self.allLights = self.args["all_lights"] # TODO change to auto array of all lights minus specifics
        self.bedroomLights = self.args["bedroom_light"]
        self.welcomeLight = self.args["welcome_light"]
        wakeupTime = self.args["wakeup_time"]
        # offTime = self.args["off_time"]
        
        self.run_daily(self.wakeup_lights, wakeupTime)
        # self.run_daily(self.speaker_power, offTime, state="off")
        self.listen_state(self._someone_home, self.home.get_home_boolean())
        self.listen_state(self._sun_lights, "sun.sun", attribute="elevation")
        self.listen_state(self.set_lightstrip_speed, "input_number.lightstrip_speed")

    def _elevation_threshold(self):
        return 4 if self.get_state("weather.jarvis") == "sunny" else 8

    def _someone_home(self, entity, attribute, old, new, kwargs):
        if not self.home.is_home():
            self.turn_off(self.allLights)
            self.log(f"User not home. Lights turned off.", level="INFO")
            return

        if self.get_state(self.welcomeLight) == "off":
            if self.get_state("sun.sun", "elevation") < self._elevation_threshold():
                self.turn_on(self.welcomeLight)
        elif self.get_state(self.welcomeLight) == "on":
            if self.get_state("sun.sun", "elevation") > self._elevation_threshold():
                self.turn_off(self.welcomeLight)

    def _sun_lights(self, entity, attribute, old, new, kwargs):
        if not self.home.is_home():
            return
        elevationThreshold = self._elevation_threshold()
        if old < elevationThreshold and new > elevationThreshold:
                self.turn_off(self.welcomeLight)
        elif old > elevationThreshold and new < elevationThreshold:
                self.turn_on(self.welcomeLight)
        
    def wakeup_lights(self, kwargs):
        # Defaults to turning off 
        if not self.home.is_home():
            self.log(f"User not home. Lights left off.", level="INFO")
            return
        self.turn_on(self.bedroomLights)
        self.log(f"Turning on morning lights.", level="INFO")

    def set_lightstrip_speed(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.lightListener.send_speed(int(float(new)))
            self.log(f"Updating lightstrip speed to {new}", level="INFO")

    def update_lightstrip(self, payload):
        if '?' in payload:
            speed = float(re.search('\?(\d+)', payload).group(1))
            oldSpeed = float(self.get_state("input_number.lightstrip_speed"))
            if oldSpeed != speed:
                self.log(f"Lightstrip speed in HA: {oldSpeed}. Speed set to: {speed}", level="DEBUG")
                self.set_value(entity_id = "input_number.lightstrip_speed", value = speed)


    # def speaker_switch_vol(self, entity, attribute, old, new, kwargs):
    #     if old == "off" and new == "on":
    #         vol = self.speakerVol
    #     elif old == "on" and new == "off":
    #         vol = self.deviceVol
    #     self.call_service("media_player/volume_set", entity_id = self.speaker, volume_level = vol)
    #     self.log(f"Speaker vol set to {vol}", level="INFO")


class LightListener(mqtt.Mqtt):
    def initialize(self):
        self.lights = self.get_app("lights")
        # Get config for notifications. For each note type, do following:
        self.listen_event(
            self.receive_speed,
            "MQTT_MESSAGE",
            namespace="mqtt",
            topic="LightStrip/out",
        )

    def receive_speed(self, event_name, data, kwargs):
        payload = data["payload"]
        self.log(
            f"lightstrip changed. MQTT Payload: '{payload}'. Topic: '{data['topic']}'.'",
            level="INFO",
        )
        self.lights.update_lightstrip(payload)

    def send_speed(self, speed):
        self.mqtt_publish(topic = "LightStrip/in", payload = "?" + str(speed))