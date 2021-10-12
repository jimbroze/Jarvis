def send_notifcation(self, notifyMessage):
        self.notifications = self.get_app("notification")
        self.notifications.send(text = notifyMessage,service = self.args["notifcationTarget"],titleText = "Location")