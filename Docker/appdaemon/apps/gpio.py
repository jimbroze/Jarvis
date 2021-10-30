import R64.GPIO as GPIO
import hassapi as hass

class ServerFan(hass.Hass):
    def initialize(self):
        self.fanPin = 5
        self.fanBoolean = "input_boolean.jarvis_fan"
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.fanPin, GPIO.OUT, initial=GPIO.LOW)
        
        temp = self.entities.sensor.processor_temperature.state
        newState = True if float(temp) > 55 else False
        self.change_fan_state(newState)

        self.listen_state(self.temp_callback, "sensor.processor_temperature")
    
    def terminate(self):
        GPIO.cleanup()

    def temp_callback(self, entity, attribute, old, new, kwargs):
        self.log(f"{new}", level="INFO")
        if float(old) < 55 and float(new) > 55:
            self.change_fan_state(True)
        elif float(old) > 45 and float(new) < 45:
            self.change_fan_state(False)
        self.log(f"temp: {new}", level="DEBUG")

    def change_fan_state(self, state=False):
        if state == True:
            gpioState = GPIO.HIGH
            self.turn_on(self.fanBoolean)
        else:
            gpioState = GPIO.LOW
            self.turn_off(self.fanBoolean)
        GPIO.output(self.fanPin, gpioState)
        fanState = GPIO.input(self.fanPin)
        if fanState != state:
            self.log(f"Fan state is {fanState} but should be {state}", level="ERROR")
