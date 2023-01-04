import paho.mqtt.client as mqtt
from time import sleep

from threading import Thread

## ToDo URL von SecondHumanFactor

class notrufMock():
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.connect("127.0.0.1", 1883, 60)
        self.notruf()
        self.client.loop_forever()
        
    def onConnect(self, client, userdata, flags, rc):
        #self.client.subscribe("signal/getTuerCode")
        None

    def onMessage(self, client, userdata, msg):
        # if msg.topic == "signal/getTuerCode":
        #     sleep(1)
        #     self.client.publish(topic="signal/setTuerCode", payload='.-.-.-...-.|........----.-.-.-..')
        None
    
    def notruf(self):
        # sleep(0.5)
        print("notruf geschickt")
        self.client.publish(topic="signal/notruf", payload='{\
                                   "id":"test123@mail.com",\
                                   "vorname":"Peter",\
                                   "nachname":"Mustermann",  \
                                  "geburtsdatum": "22.06.1960",\
                                   "strasse":"Teststraße",\
                                   "hausnummer": "1",\
                                   "plz":"20129",\
                                   "ort":"Hamburg",\
                                   "ortsteil": "",\
                                   "stockwerk":"2.OG",\
                                   "fahrstuhl":true,\
                                   "allergien":["Citrusfrüchte","Nüsse"],\
                                   "vorerkrankungen":[],\
                                   "medikation":[],\
                                   "krankenkasse":"AOK",\
                                   "versichertennummer":"3254N1",\
                                   "gewicht": 80.5,\
                                   "groesse": 175,\
                                   "position":"ja",\
                                   "bild":"ja"}')
        # for i in range(13):
        #     self.client.publish(topic="signal/heartrateping", payload='{\"heartrate\": 100}')
        #     sleep(1)
        # self.client.loop_stop()
        # sleep(5)
        # self.client.publish(topic="signal/notruf", payload='{\
        #                             "id":test@mail.com,\
        #                             "vorname":"Peter",\
        #                             "nachname":"Mustermann",  \
        #                             "geburtsdatum": "22.06.1960",\
        #                             "strasse":"Teststraße",\
        #                             "hausnummer": "1",\
        #                             "plz":"20129",\
        #                             "ort":"Hamburg",\
        #                             "ortsteil": "",\
        #                             "stockwerk":"2.OG",\
        #                             "fahrstuhl":true,\
        #                             "allergien":["Citrusfrüchte","Nüsse"],\
        #                             "vorerkrankungen":[],\
        #                             "medikation":[],\
        #                             "krankenkasse":"AOK",\
        #                             "versichertennummer":"3254N1",\
        #                             "gewicht": 80.5,\
        #                             "groesse": 175,\
        #                             "position":"F:\\alarm-test\\test.png",\
        #                             "bild":"F:\\alarm-test\\tillmad.png"\
        #                             }')


t = notrufMock()
    

    
