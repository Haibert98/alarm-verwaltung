import paho.mqtt.client as mqtt
from time import sleep

from threading import Thread

## ToDo URL von SecondHumanFactor

class klingelMock():
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.connect("127.0.0.1", 1883, 60)
        self.client.loop_forever()

    def onConnect(self, client, userdata, flags, rc):
        self.client.subscribe("signal/getTuerCode")

    def onMessage(self, client, userdata, msg):
        if msg.topic == "signal/getTuerCode":
            print("CODE ANFORDERUNG ERHALTEN")
            sleep(1)
            self.client.publish(topic="signal/setTuerCode", payload='.-.-.-...-.|........----.-.-.-..')

    
    
t = klingelMock()

    