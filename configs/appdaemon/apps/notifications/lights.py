from datetime import datetime, timedelta
import re

import hassapi as hass
import mqttapi as mqtt


class Lights(hass.Hass):
    def initialize(self):
        self.home = self.get_app("home")
        self.lightListener = self.get_app("light_listener")

        self.allLights = self.args[
            "all_lights"
        ]  # TODO change to auto array of all lights minus specifics
        self.bedroomLights = self.args["bedroom_light"]
        self.welcomeLight = self.args["welcome_light"]
        wakeupTime = datetime.strptime(self.args["wakeup_time"], "%H:%M:%S").time()
        self.wakeupDuration = self.args["wakeup_duration"] * 60
        # offTime = self.args["off_time"]

        self.run_daily(
            self.wakeup_lights, wakeupTime - timedelta(seconds=self.wakeupDuration)
        )
        # self.run_daily(self.lightstrip_power, wakeupTime)
        # self.run_daily(self.speaker_power, offTime, state="off")
        # self.listen_state(self._someone_home, self.home.get_home_boolean())
        # self.listen_state(self._sun_lights, "sun.sun", attribute="elevation")
        self.listen_state(self.set_lightstrip_speed, "input_number.lightstrip_speed")
        # self.listen_state(self.lightstrip_power, "light.lightstrip", old="on", new="off")

    def _elevation_threshold(self):
        return 4 if self.get_state("weather.jarvis") == "sunny" else 8

    def _someone_home(self, entity, attribute, old, new, kwargs):
        if not self.home.is_home():
            self.turn_off(self.allLights)
            self.turn_off("switch.lightstrip_power")
            self.log(f"User not home. Lights turned off.", level="INFO")
            return

        if self.get_state(self.welcomeLight) == "off":
            if self.get_state("sun.sun", "elevation") < self._elevation_threshold():
                self.turn_on("switch.lightstrip_power")
                self.turn_on(self.welcomeLight)
        elif self.get_state(self.welcomeLight) == "on":
            if self.get_state("sun.sun", "elevation") > self._elevation_threshold():
                self.turn_off(self.welcomeLight)

    def wakeup_lights(self, kwargs):
        # Defaults to turning off
        if self.get_state(self.welcomeLight) == "on":
            self.log(f"Wakeup light is already on.", level="INFO")
            return
        if not self.home.is_home():
            self.log(f"User not home. Wakeup light left off.", level="INFO")
            return
        self.turn_on(
            self.bedroomLights, transition=self.wakeupDuration, brightness_pct=100
        )
        # self.turn_on("switch.lightstrip_power")
        self.log(f"Turning on morning lights.", level="INFO")

    def _sun_lights(self, entity, attribute, old, new, kwargs):
        if not self.home.is_home():
            return
        elevationThreshold = self._elevation_threshold()
        if old < elevationThreshold and new > elevationThreshold:
            self.turn_off(self.welcomeLight)
        elif old > elevationThreshold and new < elevationThreshold:
            self.turn_on(self.welcomeLight)

    def set_lightstrip_speed(self, entity, attribute, old, new, kwargs):
        if new != old:
            self.lightListener.send_speed(int(float(new)))
            self.log(f"Updating lightstrip speed to {new}", level="INFO")

    def update_lightstrip(self, payload):
        if "?" in payload:
            speed = float(re.search("\?(\d+)", payload).group(1))
            oldSpeed = float(self.get_state("input_number.lightstrip_speed"))
            if oldSpeed != speed:
                self.log(
                    f"Lightstrip speed in HA: {oldSpeed}. Speed set to: {speed}",
                    level="DEBUG",
                )
                self.set_value(entity_id="input_number.lightstrip_speed", value=speed)

    def lightstrip_power(
        self, entity=None, attribute=None, old=None, new=None, kwargs=None
    ):
        if new == "off":
            if self.now_is_between("22:15:00", "06:15:00", name=None):
                self.turn_off("switch.lightstrip_power")
        # else:
        #     self.turn_on("switch.lightstrip_power")
        #     self.turn_off("light.lightstrip")


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
            (
                f"lightstrip changed. MQTT Payload: '{payload}'. Topic:"
                f" '{data['topic']}'.'"
            ),
            level="INFO",
        )
        self.lights.update_lightstrip(payload)

    def send_speed(self, speed):
        self.mqtt_publish(topic="LightStrip/in", payload="?" + str(speed))
