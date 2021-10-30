import R64.GPIO as GPIO
import hassapi as hass

class ServerFan(hass.Hass):
    def initialize(self):
        self.fanPin = 5
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.fanPin, GPIO.OUT, initial=GPIO.LOW)

        self.log(f"{GPIO.input(self.fanPin)}", level="DEBUG") 

        self.listen_state(self.temp_callback, "sensor.processor_temperature")
    
    def terminate(self):
        GPIO.cleanup()

    def temp_callback(self, entity, attribute, old, new, kwargs):
        if float(old) < 55 and float(new) > 55:
            self.change_fan_state(True)
        elif float(old) > 45 and float(new) < 45:
            self.change_fan_state(False)
        self.log(f"temp: {new}", level="DEBUG")

    def change_fan_state(self, state=False):
        gpioState = {False: GPIO.LOW, True: GPIO.HIGH}[state]
        GPIO.output(self.fanPin, gpioState)
        fanState = GPIO.input(self.fanPin)
        self.set_value(self.fanBoolean, fanState)
        self.log(f"fanState: {fanState}", level="INFO")
