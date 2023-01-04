import paho.mqtt.client as mqtt
import time
from random import randrange
from _thread import start_new_thread
import json


ZEIT_CODE_VERFUEGBAR = 30 #Minuten zahl die der code verfuegbar sein soll
LEDTIMER = 3 #Dauer in s die die LED an ist bei Reset und oeffnen
LEDTIMER_KURZ = 0.1
LEDTIMER_LANG = 0.5
RESET_DAUER = 3 #Dauer die der Knopf zum Resetten der Eingabe gedrueckt werden muss


MQTT_HOST_LP = "dashboard.lp.smsy.haw-hamburg.de"#"broker.hivemq.com"
MQTT_PORT_LP = 1901#1883


class TsVerwalter:
    def __init__(self, client):
        self.bitCounter = 0
        self.codeEingabe = 0
        self.codeTuer = None
        self.errorCounter = 0
        self.backupCodeTuer = None
        self.tsCodeAv = None
        self.tsDifferences = []
        self.client = client

    #Thread schlaeft solange ein Code verfuegbar ist, anschliessendes verwerfen des Codes
    #sleeptime+1, damit wir sicher gehen dass immer länger geschlafen wird als der Code verfügbar ist und es nicht um millisekunden geht
    def doorAvailability(self, sleeptime):
        print("Code verfuegbar fuer {} Minuten".format(str((sleeptime+1) * 60 / 60)))
        time.sleep((sleeptime+1) * 60)
        zeitDif = time.time() - self.tsCodeAv #Zeit die von letzter anfordeungen vergangen ist
        if((zeitDif - ((sleeptime+1) * 60)) > 0.0): #es gab keine neue Anforderung eines Codes waehrend geschlafen wurde
            print("zeitDif war groesser -> Aufraeumen")
            self.codeTuer = None
            self.backupCodeTuer = None
        else: #es wurde zwischendurch ein neuer Code angefordert
            print("Zeit verlaengert, Code noch verfuegbar fuer: {} Minuten".format(zeitDif))
            self.doorAvailability(zeitDif)

    #Wenn Code nach 4s gleich->oeffnen, sonst nicht oeffnen
    def opendoor(self):
        print("Ueberpruefe Code")
        time.sleep(4)
        if((self.codeTuer == self.codeEingabe and self.bitCounter == 5)  or 
            (self.backupCodeTuer == self.codeEingabe and self.bitCounter == 10)):
            print("Öffne Tür")
            self.bitCounter = 0
            self.codeEingabe = 0
            self.errorCounter = 0
            self.tsDifferences = []
            self.client.publish(topic="lp/flur/schloss/set", payload="1", qos=2)
            self.client.publish(topic="signal/klingel/led", payload="gruen", qos=2)
            start_new_thread(self.sendeLEDclear, (LEDTIMER,))#schaltet die LED wieder aus
        else: 
            print("ABGELEHNT, Eingabe: {}, aktuellerCode: {}".format(self.formatiereZuMorsecode(self.codeEingabe, False),self.formatiereZuMorsecode(self.codeTuer, True)))

    #Fuegt fuehrende 0en hinzu wenn Code mit "kurz" anfaengt (da diese bei Umwandlung int->str nicht übernommen werden)
    def addLeadingZeroes(self, code):
        if len(code) == 5 or len(code) == 10:
            return code
        else:   
            return self.addLeadingZeroes("0" + code)
    
    #Parst code von interner Speicherart zu Morsecodezeichen
    #Beispiel: 01101 zu -.--.
    def formatiereZuMorsecode(self, code ,beideCodes=False):
        code = format(code, 'b')
        code = self.addLeadingZeroes(str(code))
        code = code.replace("1", "-" ).replace("0", ".")[::-1]
        backupCode = format(self.backupCodeTuer, 'b')
        backupCode = self.addLeadingZeroes(str(backupCode))
        backupCode = backupCode.replace("1", "-" ).replace("0", ".")[::-1]
        if beideCodes:
            return "{}|{}".format(code,backupCode)
        else:
            return str(code)
    
    #schlaeft fuer timer sekunden und sendet anschliessend das Signal um die LED der Klingel auszuschalten
    def sendeLEDclear(self, timer):
        time.sleep(timer)
        self.client.publish(topic="signal/klingel/led", payload="clear", qos=2)

    #Wertet die in tsDifferences gespeicherten Drueckdauern aus (Jede Dauer bekommt als value Lang oder Kurz), was in tsverwalter.codeEingabe gespeichert wird
    def checkEingabe(self):
            minval = int(min(self.tsDifferences))
            maxval = int(max(self.tsDifferences))
            mittelwert = minval + ((maxval-minval)/2.0)
            for value in self.tsDifferences:
                self.kurzEintragen() if int(value)<mittelwert else  self.langEintragen()
            start_new_thread(self.opendoor, ())#prueft ob code richtig war und sendet topic
    
    #Wenn Dauer als Kurz zählt
    def kurzEintragen(self):
        if(self.bitCounter == 0):
            self.codeEingabe = 0
        self.bitCounter += 1

    #Wenn Dauer als Lang zählt
    def langEintragen(self):
        self.codeEingabe += (2 ** self.bitCounter)
        self.bitCounter += 1

class MqttMethods:
    def __init__(self,tsverwalter, client):
        self.tsverwalter = tsverwalter
        self.client = client
       
    #MQQT on connect
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    #Baut ein JSON-File in dieser Art: {"email": "bei@spiel.com", "doorCode": "..--.", "backupCode": "--...-.-.."}
    def buildJSON(self, payload):
        payload = payload.replace("\'", "\"")#falls erhaltenne JSON ' statt " benutzt
        data = json.loads(payload)
        
        newPayload = {}
        newPayload["email"] = data["email"]
        newPayload["doorCode"] = self.tsverwalter.formatiereZuMorsecode(self.tsverwalter.codeTuer, False)
        newPayload["backupCode"] = self.tsverwalter.formatiereZuMorsecode(self.tsverwalter.backupCodeTuer, False)

        return str(newPayload).replace("\'","\"")

    #Eingang von MQTT-Events
    #signal/getTuerCode:
    #Liefert einen Tuercode der ab Aufruf ZEIT_CODE_VERFUEGBAR Minuten lang gilt
    #Gibt den aktuellen zurueck falls bereits einer existiert
    #signal/klingel
    #Wertet ein Klingelevent (High->Low oder Low->High aus)
    def on_message(self, client, userdata, msg):
        if(msg.topic == "signal/getTuerCode" or msg.topic == "door/getcode"):
            print("CodeErstellen Topic erhalten: " + msg.payload.decode())
            self.tsverwalter.tsCodeAv = time.time()#Anfragezeit speichern um Verfallszeitpunkt berechnen zu koennen
            if(self.tsverwalter.codeTuer == None):#Es gibt nur einen gueltigen Code zur Zeit
                #Code erstellen
                self.tsverwalter.codeTuer = randrange(1,31) # nur Kurz und nur Lang sind ausgeschlossen
                self.tsverwalter.backupCodeTuer = randrange(1,1023)
                print("Created Codes: " + str(self.tsverwalter.codeTuer) + " and " + str(self.tsverwalter.backupCodeTuer))
                start_new_thread(self.tsverwalter.doorAvailability, (ZEIT_CODE_VERFUEGBAR,)) #Tuercode nach bestimmter Zeit ungueltig
            if (msg.topic == "signal/getTuerCode"):
                self.client.publish(topic="signal/setTuerCode", payload=self.tsverwalter.formatiereZuMorsecode(self.tsverwalter.codeTuer, beideCodes=True), qos=2)
            else:
                self.client.publish(topic="door/code", payload = self.buildJSON(msg.payload.decode()), qos=2)
            print("published")
        if(msg.topic == "signal/klingel"):
            newestTsDifference = msg.payload.decode()
            print("neuste Differenz: {}".format(newestTsDifference))
            if(int(newestTsDifference)>=RESET_DAUER*1000000):#laenger als 3s ist ein reset
                print("RESET")
                self.tsverwalter.bitCounter = 0
                self.tsverwalter.codeEingabe = 0
                self.tsverwalter.tsDifferences = []
                self.tsverwalter.errorCounter += 1
                print("ErrorCounter: {}".format(self.tsverwalter.errorCounter))
                self.client.publish(topic="signal/klingel/led", payload="rot", qos=2)
                start_new_thread(self.tsverwalter.sendeLEDclear, (LEDTIMER,))#schaltet die LED wieder aus
            else:#Drueckdauer in Liste speichern
                self.tsverwalter.tsDifferences.append(newestTsDifference)
            if ((len(self.tsverwalter.tsDifferences)==5 and self.tsverwalter.errorCounter<10) or 
                    (len(self.tsverwalter.tsDifferences)==10 and self.tsverwalter.errorCounter>=10)):#wenn 5-langer Code gilt und 5 eingegeben wurden: ueberpruefe, gleiches fuer langen falls dieser gilt
                print("Gonna check Eingabe")
                self.tsverwalter.checkEingabe()
        if(msg.topic == "signal/setTuercodeManuell"):
            self.tsverwalter.tsCodeAv = time.time()#Anfragezeit speichern um Verfallszeitpunkt berechnen zu koennen

            msg = msg.payload.decode()
            data = json.loads(msg)
            code = int(data["code"])
            backupCode = int(data["backupCode"])

            self.tsverwalter.codeTuer = code if code<31 and code>0 else 21
            self.tsverwalter.backupCodeTuer = backupCode if backupCode<1023 and backupCode>0 else 844
            if self.tsverwalter.codeTuer == None:
                start_new_thread(self.tsverwalter.doorAvailability, (ZEIT_CODE_VERFUEGBAR,)) #Tuercode nach bestimmter Zeit ungueltig
            print("Manuellercode: {}".format(self.tsverwalter.formatiereZuMorsecode(self.tsverwalter.codeTuer, True)))


def runClient(client):
    client.loop_forever()

def runTuerCodeVerwalter():
    clientLP = mqtt.Client()

    tsverwalter = TsVerwalter(clientLP) 

    mqttMethods = MqttMethods(tsverwalter, clientLP)

    clientLP.on_connect = mqttMethods.on_connect
    clientLP.on_message = mqttMethods.on_message
    clientLP.connect(MQTT_HOST_LP, MQTT_PORT_LP, 60)

    clientLP.on_connect = mqttMethods.on_connect
    clientLP.on_message = mqttMethods.on_message
    clientLP.connect(MQTT_HOST_LP, MQTT_PORT_LP, 60)
    clientLP.subscribe("signal/klingel", qos=2)
    clientLP.subscribe("signal/getTuerCode", qos=2)
    clientLP.subscribe("door/getcode", qos=2)
    clientLP.subscribe("signal/setTuercodeManuell", qos=2) 
    

    #start_new_thread(runClient, (clientLP,))
    clientLP.loop_forever()#einkommentieren wenn Modul einzeln laueft, da sonst die Threads beendet werden, auskommentieren wenn von anderem Modul aufgerufen
    
runTuerCodeVerwalter()