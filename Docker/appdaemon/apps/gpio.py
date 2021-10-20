import R64.GPIO as GPIO

import hassapi as hass

class ServerFan(hass.Hass):
    def initialize(self):
        self.fanPin = 16
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.fanPin, GPIO.OUT, initial=GPIO.LOW)
        # 55 and 45

        self.listen_state(self.temp_callback, "sensor.processor_temperature")

    def temp_callback(self, entity, attribute, old, new, kwargs):
        # if old < 55 and new > 55:
        #     self.change_fan_state(True)
        # elif old > 45 and new < 45:
        #     self.change_fan_state(False)
        self.log(f"{new}", level="ERROR")
        self.log(f"{new}", level="DEBUG")

    def change_fan_state(self, state=False):
        gpioState = {False: GPIO.LOW, True: GPIO.HIGH}[state]
        GPIO.output(self.fanPin, gpioState)
        fanState = GPIO.input(self.fanPin)              