from threading import Thread
from Kommunikation.sms import SMSController
from Kommunikation.fax import FAXController

class Controller:
    def __init__(self):
        #self.msgData = msgData
        #self.link = link
        #self.tuerCode = tuerCode
        self.smsCnt = SMSController()
        self.faxCnt = FAXController()

    def sendAlarm(self, msgData, link):
        sms = self.smsCnt.parseSMS(msgData, link)
        response = self.smsCnt.sendSMS(sms)
        
        if response:
            return True  # Hier muss das System benachrichtig werden
        else:
            return self.faxCnt.buildPDF(msgData, link)

