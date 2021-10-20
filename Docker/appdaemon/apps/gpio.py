import R64.GPIO as GPIO

import hassapi as hass

class ServerFan(hass.Hass):
    def initialize(self):
        self.fanPin = 16
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.fanPin, GPIO.OUT, initial=GPIO.LOW)

        print("")
        print("Module Variables:")
        print("Name           Value")
        print("----           -----")
        print("GPIO.ROCK      " + str(GPIO.ROCK))
        print("GPIO.BOARD     " + str(GPIO.BOARD))
        print("GPIO.BCM       " + str(GPIO.BCM))
        print("GPIO.OUT       " + str(GPIO.OUT))
        print("GPIO.IN        " + str(GPIO.IN))
        print("GPIO.HIGH      " + str(GPIO.HIGH))
        print("GPIO.LOW       " + str(GPIO.LOW))
        print("GPIO.PUD_UP    " + str(GPIO.PUD_UP))
        print("GPIO.PUD_DOWN  " + str(GPIO.PUD_DOWN))
        print("GPIO.VERSION   " + str(GPIO.VERSION))
        print("GPIO.RPI_INFO  " + str(GPIO.RPI_INFO))

        self.log(f"{GPIO.input(self.fanPin)}", level="ERROR") 

        self.listen_state(self.temp_callback, "sensor.processor_temperature")
    
    def terminate(self):
        GPIO.cleanup()

    def temp_callback(self, entity, attribute, old, new, kwargs):
        if float(old) < 55 and float(new) > 55:
            self.change_fan_state(True)
        elif float(old) > 45 and float(new) < 45:
            self.change_fan_state(False)
        self.log(f"{new}", level="DEBUG")

    def change_fan_state(self, state=False):
        gpioState = {False: GPIO.LOW, True: GPIO.HIGH}[state]
        GPIO.output(self.fanPin, gpioState)
        fanState = GPIO.input(self.fanPin)              