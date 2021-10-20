import R64.GPIO as GPIO

import hassapi as hass

class ServerFan(hass.Hass):
    def initialize(self):
        self.fanPin = 16
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.fanPin, GPIO.OUT, initial=GPIO.LOW)
        # 55 and 45

    def change_fan_state(self, state=False):
        gpioState = {False: GPIO.LOW, True: GPIO.HIGH}[state]
        GPIO.output(self.fanPin, gpioState)
        fanState = GPIO.input(self.fanPin)               