import R64.GPIO as GPIO

import hassapi as hass

class ServerFan(hass.Hass):
    def initialize(self):
        self.fanPin = 5

        fanTemp = float(self.entities.sensor.processor_temperature.state)
        gpioState = GPIO.HIGH if fanTemp > 55 else GPIO.LOW
        
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.fanPin, GPIO.OUT, initial=gpioState)

        self.listen_state(self.temp_callback, "sensor.processor_temperature")
    
    def terminate(self):
        GPIO.cleanup()

    def temp_callback(self, entity, attribute, old, new, kwargs):
        self.log(f"{new}", level="INFO")
        if float(old) < 55 and float(new) > 55:
            self.change_fan_state(True)
        elif float(old) > 45 and float(new) < 45:
            self.change_fan_state(False)

    def change_fan_state(self, state=False):
        gpioState = {False: GPIO.LOW, True: GPIO.HIGH}[state]
        GPIO.output(self.fanPin, gpioState)
        fanState = GPIO.input(self.fanPin) 
        self.set_value("input_boolean.jarvis_fan", fanState)
        self.log(f"{fanState}", level="INFO")