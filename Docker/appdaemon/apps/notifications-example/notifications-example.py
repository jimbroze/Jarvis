import hassapi as hass
import random
import time
import globals

class Notifications(hass.Hass):
    notification_targets = []   
    def initialize(self):
        Notifications.notification_targets = ["dummy"]
        self.sound = self.get_app("ttssound")
        for target in self.args["notification_targets"]:
            Notifications.notification_targets.append(target)
        
    def send(self, text, service = "00",titleText = "Notification", threadID = "HA"):
        """
        This function will take a 2 number binanry number and send messages to the numbers set as 1
        first number = Mobile Phones
        second number = TTS Services as defined in Sound
        """

        targetService = ""
        targetFlag = 0
        notificationQueue = []
        notificationQueue.clear()

        self.log(text)
        # Check first Number - this is for mobile notifcations
        if service[0] == "0":
            notificationQueue.clear()  
        elif service[0] == "6":
           for target_service in Notifications.notification_targets:
               notificationQueue.append(target_service)
        else:
            target_service = Notifications.notification_targets[int(service[0])]
            notificationQueue.append(target_service)
  

        #Send Message
        if service[0] != "0" or service[0] != 0:
          for notification in notificationQueue:
            try:  
              self.call_service(service = notification, title = titleText, message = text , data = {"push":{"thread-id": threadID}})
              logMessage = " {} sent to {}". format(text, notification)
              self.log(logMessage)

            except:
              self.log("Error: Notification Service")
              self.log(notification)
              #self.log(sys.exc_info()) 
        else:
            self.log("No mobile notification service selected")

        # Check second Number. Use the number provided to map to the TTS service in Class Sound
        if service[1] != "0" or service[1] != 0:
            self.sound = self.get_app("ttssound")
            # add some letters to the the service to account for more than 9 Speakers
            if service[1] == "A":
               TTS_service = 10
            elif service[1] == "B":
               TTS_service = 11
            elif service[1] == "C":
               TTS_service = 12
            elif service[1] == "D":
               TTS_service = 13      
            else:   
               TTS_service = int(service[1])
            
            #self.log(TTS_service)
            self.sound.tts(text, len(text)/11, speaker = TTS_service)  
        else:
            return