import paho.mqtt.client as mqtt
import json
import os
# from ..Webseite.templateEngine import WebSiteTemplateEngine
from Webseite.templateEngine import WebSiteTemplateEngine
from Kommunikation.controller import Controller
from MQTT_HTTP.mqtthttp import MQTPConverter
from threading import Timer, Thread, Lock, Condition
import matplotlib.pyplot as plt
import time
from datetime import datetime
BROKERNAME = "127.0.0.1"
BROKERPORT = 1883
#------------------------------------------------
#   AlarmVerwaltung: Diese Klasse nimmt Daten entgegen, stoesst die notwendigen Komponenten
#                    an und aktualisiert die visualisierten Daten.
#                    Anschliessend wird der Status der Alarmierung zurueckgemeldet
#   Authors:         Haidar Mortada, Stefan Sachmann
#------------------------------------------------
class AlarmVerwaltung:
    def __init__(self):
        self.picDir = '/home/projectuser/projectlp/photos'   # Subordner fuer Bilder
        self.locDir = '/home/projectuser/projectlp/location' # Subordner fuer Karte
        self.webTE = WebSiteTemplateEngine(self.picDir, self.locDir)        # Website-Komponente
        self.controller = Controller()              # Kommunikation
        self.mqtpConv = MQTPConverter()             # MQTT-HTTP-Converter
        self.client = mqtt.Client()
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.connect(BROKERNAME, BROKERPORT, 60)
        self.heartBeatMtx = Lock()
        self.heartBeatCV = Condition(lock=self.heartBeatMtx)
        self.heartBeatWerte = []
        self.heartBeatTS = []
        self.heartBeatCnt = 0
        self.heartBeatBereit = False
        self.mqttMtx = Lock()                       # Mutex fuer Pruefung der Alarmierung
        self.mqttCV = Condition(lock=self.mqttMtx)  # Condition Variable mit Mutex
        self.alarmierungDa = False                  # Alarmierung reingekommen?
        # self.vorfallID = None                       # Unique ID
        self.dataMqtt = None
        self.alarmDataJSON = None                       # Alarm Daten (Dict)
        self.tuerCodeDa = False                     # Variable fuers Blockieren
        self.link = None                            # Link der Website
        self.response = ""
        #ToDo funktioniert das so mit subOrdner wegen Position und Bilder?
        # self.webTimer = None #Timer(3600.0, self.cleanUp) # Timer fuer Clean Up   (1 Std)
        handlerThread = Thread(target=self.parseData, args=())
        mqttThread = Thread(target=self.client.loop_forever, args=())
        heartbeatThread = Thread(target=self.heartBeatDrawer, args=())
        handlerThread.start()
        mqttThread.start()
        heartbeatThread.start()
        


    def onConnect(self, client, userdata, flags, rc):
        print("MQTTCLIENT gestartet")
        client.subscribe("signal/notruf")
        client.subscribe("signal/heartrateping")
        client.subscribe("signal/setTuerCode")

    def onMessage(self, client, userdata, msg):
        if msg.topic == "signal/notruf":
            self.mqttMtx.acquire()
            self.dataMqtt = msg.payload.decode()
            self.alarmierungDa = True
            self.mqttCV.notify_all()
            self.mqttMtx.release()
            print("Notruf erhalten")
        elif msg.topic == "signal/heartrateping":
            self.heartBeatMtx.acquire()
            tmp = json.loads(msg.payload.decode())
            self.heartBeatCnt += 1
            self.heartBeatWerte.append(int(tmp["heartrate"]))
            self.heartBeatTS.append(datetime.strftime(datetime.now(), '%H:%M:%S'))
            if self.heartBeatCnt % 12 == 0:
                self.heartBeatCnt = 0
                # os.system("python ./Alarm_Verwaltung/heartbeatgraph.py " + str(self.heartBeatWerte) + ", " +  str(self.heartBeatTS))
                self.heartBeatBereit = True
                self.heartBeatCV.notify_all()
            self.heartBeatMtx.release()
        elif msg.topic == "signal/setTuerCode":
            self.tuerCode = msg.payload.decode()
            self.tuerCodeDa = True
            

    def parseData(self):
        print("Handler gestartet")
        while True:
            with self.mqttMtx:
                while not self.alarmierungDa:
                    self.mqttCV.wait()          # Warten auf Alarmierung
                self.alarmierungDa = False      # Zuruecksetzen, um wieder zu schlafen
            if self.dataMqtt:                   # waren da wirklich daten?
                self.alarmDataJSON = json.loads(self.dataMqtt)
                self.dataMqtt = None
            else:
                raise
            if self.alarmDataJSON["update"]:     #Update zum Vorfall
                print("UPDATE")
                self.updateData()        ## Update der Daten
            else:   
                print("ALARM")
                self.startAlarm()

    def updateData(self):
        self.webTE.updateWebsite(self.alarmDataJSON)        # Update Website
    
    def startAlarm(self):
        # self.vorfallID = self.alarmDataJSON["email"]       # Neuer Vorfall
        self.client.publish("signal/getTuerCode", payload= b'')
        while not self.tuerCodeDa:      # Warten auf TuerCode
            None
        self.link = self.webTE.createWebSite(self.alarmDataJSON, self.tuerCode)     # Erstellen der Website
        print(self.link)
        # if self.webTimer:
        #     self.webTimer.cancel()
        #     self.cleanUp()
        #     self.webTimer = self.getTimer()
        # else:
        #     self.webTimer = self.getTimer()
        # self.webTimer.start()           # Timer Starten
        
        res = self.controller.sendAlarm(self.alarmDataJSON, self.link, self.tuerCode)  # Alarmieren
        print("Alarmierung erfolgreich: " + str(res))
        response = ""
        if res:
            response = '{ "status": true }'
        else:
            response = '{ "status" : false }'
        print(response)
        print(json.loads(response))
        self.client.publish(topic="signal/notruferfolgt", payload=self.response.encode("utf8"))                       # Ruckmeldung der Alarmierung

    # def cleanUp(self):
    #     self.webTE.deleteWebsite()      # Website loeschen
    #     if os.path.exists(self.picDir):    # Bilder loeschen
    #         for file in os.listdir(self.picDir):
    #             os.remove(os.path.join(self.picDir, file))
    #     if os.path.exists(self.locDir):    # Karte loeschen
    #         for file in os.listdir(self.locDir):
    #             os.remove(os.path.join(self.locDir, file))

    # def getTimer(self):
    #     return Timer(3600.0, self.cleanUp)

    def heartBeatDrawer(self):
        while True:
            with self.heartBeatCV:
                while not self.heartBeatBereit:
                    self.heartBeatCV.wait()
                os.system("python ./Alarm_Verwaltung/heartbeatgraph.py " + 
                            str(self.heartBeatWerte) + ", " +  str(self.heartBeatTS))    
                self.heartBeatBereit = False