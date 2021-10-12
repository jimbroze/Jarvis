import appdaemon.plugins.hass.hassapi as hass
from queue import Queue
from threading import Thread
from threading import Event
import time
import globals



#
# App to manage announcements via TTS to Google Home
#
# Provides methods to enqueue TTS and Media file requests and make sure that only one is executed at a time
# Volume of the media player is set to a specified level and then restored afterwards
#
# Args:
#
# speaker: media player to use for announcements
# TTSVolume: media played volume 0-1

class Sound(hass.Hass):
  Sound.speakers = [] 
  def initialize(self):
    Sound.speakers = ["dummy"]
    # Create Queue
    self.queue = Queue(maxsize=0)

    # Create worker thread
    t = Thread(target=self.worker)
    t.daemon = True
    t.start()
    self.event = Event()
    self.log("Thread Alive {}, {}" .format (t.isAlive(), t.is_alive()))
    for speaker in self.args["speakers"]:
      Sound.speakers.append(speaker)
    self.log(Sound.speakers)

  def worker(self):
    while True:
      try:
        # Get data from queue
        data = self.queue.get()
        self.log(" This is has been pulled off the current Queue {}".format(data))

        if data["type"] == "terminate":
          active = False
        else:
          current_speaker = Sound.speakers[int(data["speaker"])]

          if self.now_is_between(globals.TTSStart, globals.TTSFinish):
            # Save current volume
            volume = self.get_state(current_speaker, attribute="volume_level")
            self.log("Current Volume save {}".format(volume))

            # Turn on Google and Set to the desired volume
            self.call_service("media_player/turn_on", entity_id = current_speaker)
            self.call_service("media_player/volume_set", entity_id = current_speaker, volume_level = self.args["TTSVolume"])
            self.log("Set the Volume to {}".format(self.args["TTSVolume"]))
            
            # Call TTS service
            self.call_service("tts/google_translate_say", entity_id = current_speaker, message = data["text"])
            self.log("This is the text said - {}".format(data["text"]))
            
            # Sleep to allow message to complete before restoring volume
            self.log("Now sleep for {}".format(int(data["length"])))
            time.sleep(int(data["length"])+3)
            
            # Restore volume
            self.call_service("media_player/volume_set", entity_id = current_speaker, volume_level = volume)
            self.log("Restore Volume")

            # Set state locally as well to avoid race condition
            ##self.set_state(self.args["player"], attributes = {"volume_level": volume})
      except:  
        self.log("Error")
        #self.log(sys.exc_info())
      
      self.queue.task_done()
      
    self.log("Worker thread exiting")
    self.event.set()
       
  def tts(self, text, length, speaker = 0):
    if self.now_is_between(globals.TTSStart, globals.TTSFinish) and speaker !=0 :
       self.queue.put({"type": "tts","text": text, "length": length, "speaker": speaker})

  def terminate(self):
    self.event.clear()
    self.queue.put({"type": "terminate"})
    self.log(" Terminate function called")
    self.event.wait()