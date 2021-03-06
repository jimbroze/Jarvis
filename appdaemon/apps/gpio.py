import R64.GPIO as GPIO
import hassapi as hass

class ServerFan(hass.Hass):
    def initialize(self):
        self.fanPin = self.args["pin"]
        self.high = self.args["high_temp"]
        self.low = self.high - self.args["delta"]
        self.fanBoolean = self.args["fanBoolean"]
        self.tempSensor = self.args["tempSensor"]
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.fanPin, GPIO.OUT, initial=GPIO.LOW)
        
        newState = True if float(self.get_state(self.tempSensor)) > self.high else False
        self.change_fan_state(newState)

        self.listen_state(self.temp_callback, self.tempSensor)
        self.listen_state(self.fan_callback, self.fanBoolean)
    
    def terminate(self):
        GPIO.cleanup()

    def temp_callback(self, entity, attribute, old, new, kwargs):
        if float(old) < self.high and float(new) > self.high:
            self.change_fan_state(True)
        elif float(old) > self.low and float(new) < self.low:
            self.change_fan_state(False)
        self.log(f"temp: {new}", level="DEBUG")

    def fan_callback(self, entity, attribute, old, new, kwargs):
        newFanState = {"on": True, "off": False}[new]
        currentFanState = GPIO.input(self.fanPin)
        if currentFanState != newFanState:
            self.change_fan_state(newFanState)

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
