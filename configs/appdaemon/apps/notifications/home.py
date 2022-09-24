# from datetime import datetime

import hassapi as hass


class Home(hass.Hass):
    def initialize(self):

        self.homeBoolean = self.args["home_boolean"]
        self.users = self.args["users"]

        # self.run_daily(self.speaker_power, "09:30:00", state="on")

        for user in self.users:
            self.log(f"{user} logging", level="INFO")
            self.listen_state(self._update_boolean, user)
        
        self._update_boolean()

    def is_home(self, entity="", attribute="", old="", new="", kwargs=""):
        # Defaults to False unless specifically "on"
        return self.get_state(self.homeBoolean) == "on"

    def get_home_boolean(self):
        return self.homeBoolean

    def _update_boolean(self, entity="", attribute="", old="", new="", kwargs=""):
        oldState = self.get_state(self.homeBoolean)
        newState = "off"
        for user in self.users:
            if self.get_state(user) == "home":
                newState = "on"
                self.log(f"{user} is at home.", level="INFO")
                break
        if oldState != newState:
            self.turn_on(self.homeBoolean) if newState == "on" else self.turn_off(self.homeBoolean)
            self.log(f"Home boolean set to {newState}.", level="INFO")
        else:
            self.log(f"Home boolean already set to {newState}.", level="INFO")