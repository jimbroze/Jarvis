# from datetime import datetime

import hassapi as hass


class Home(hass.Hass):
    def initialize(self):

        self.homeBoolean = self.args["home_boolean"]
        self.users = self.args["users"]

        # self.run_daily(self.speaker_power, "09:30:00", state="on")

        for user in self.users:
            self.listen_state(self._update_boolean, user)

    def is_home(self, entity="", attribute="", old="", new="", kwargs=""):
        # Defaults to False unless specifically "on"
        return self.get_state(self.homeBoolean) == "on"

    def get_home_boolean(self):
        return self.homeBoolean

    def _update_boolean(self, entity, attribute, old, new, kwargs):
        for user in self.users:
            if self.get_state(user) == "home":
                self.turn_on(self.homeBoolean)
                return
        # Default to off unless someone "home"
        self.turn_off(self.homeBoolean)