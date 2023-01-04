import json
from threading import Lock
from threading import Condition
import socket
from threading import Thread
TCPSERVERADD= ("192.168.167.153", 4445)

class SMSController:
    def __init__(self):
        self.udpPort = 4446
        self.udpAddress= "192.168.167.54"
        self.clientSocket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.serverSocket = None
        self.warteMtx = Lock()
        self.warteCV = Condition(lock=self.warteMtx)
        self.smsOk = False
        self.datagramOk = False
        self.threadMtx = Lock()
        self.threadVar = True

    def parseSMS(self, data, link):
        try:
            personenzustand = data["personenzustand"]
            bewusstsein = ""
            if personenzustand:
                bewusstsein = "ansprechbar"
            else:
                bewusstsein = "ohnmächtig"
        except KeyError:
            bewusstsein = ""
        ret = ""
        if bewusstsein:
            ret = "Rettung zu {} {},Adr.{} {},{} {},{}\n" \
                    "Person {}\n" \
                    "Infos auf:{}".format(data["vorname"], data["nachname"], data["strasse"], data["hausnummer"], data["plz"], data["ort"], data["stockwerk"], bewusstsein, link)
        else:
            ret = "Rettung zu {} {},Adr.{} {},{} {},{}\n" \
                    "Infos auf:{}".format(data["vorname"], data["nachname"], data["strasse"], data["hausnummer"], data["plz"], data["ort"], data["stockwerk"], link)
        # print(len(ret))
        return ret  # wer meldet fehlt noch, undmorsecode sollte aber am besten auf die website

    def sendSMS(self, msg):
        bufSize = 1024
        bytes = bytearray(msg.encode("utf-8"))
        t = Thread(target=self.connectTCP, args=[bytes])
        t.start()                     
        with self.warteCV:
            while not self.smsOk:
                tmp = self.warteCV.wait(timeout=10.0)
                if not tmp:
                    self.smsOk=False
                    break
        print("Sms " + str(self.smsOk))   # delete plz
        return self.smsOk
    
    def connectTCP(self, bytes):
        try:
            self.clientSocket.connect(TCPSERVERADD)
        except TimeoutError:
            print("TCP Connection Timeout!!\n")
            return
        bytes.append(0x05)
        self.clientSocket.send(bytes)
        # response = self.clientSocket.makefile("r", encoding='utf8', newline='\r\n')
        while True:
            data = self.clientSocket.recv(50)
            if b'sms gesendet5' == data:
                with self.warteCV:
                    self.smsOk = True
                    self.warteCV.notify_all()
                    self.clientSocket.close()
                    break
