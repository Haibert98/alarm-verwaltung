import paho.mqtt.client as mqtt
import socket
import requests
from threading import Thread
import ast
import json
## ToDo URL von SecondHumanFactor
MQTTBROKER = "127.0.0.1"#dashboard.lp.smsy.haw-hamburg.de"
MQTTPORT = 1883 # 1901
class MQTPConverter():
    def __init__(self):
        self.TOMQTT = ["signal/personaldata", "door/getcode"]
        self.TOHTTP = ["signal/initstart", "signal/initstartemergency", "signal/notruferfolgt", 
                            "door/code", "picture/turtech", "signal/heartrateping"]
        self.url = 'http://127.0.0.1:1880'
        self.port = 42069
        self.socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # self.sslCtx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.client = mqtt.Client()
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        self.client.connect(MQTTBROKER, MQTTPORT, 60)
        t1 = Thread(target= self.client.loop_forever, args=())
        t2 = Thread(target= self.tcpServer, args=[self.port])
        t1.start()
        t2.start()

    def onConnect(self, client, userdata, flags, rc):
        self.client.subscribe([("signal/heartrateping", 0), ("signal/notruferfolgt", 0), ("signal/initstart", 0), 
                                    ("signal/initstartemergency", 0), ("door/code", 0),("picture/turtech", 0) ])

    def onMessage(self, client, userdata, msg):
        #print(msg.payload)
        if msg.topic in self.TOHTTP:
            self.mqttTohttp(msg)
    
    def tcpServer(self, port):
        self.socket.bind(('', port))
        self.socket.listen()
        while True:
            conx, addr = self.socket.accept()
            self.handleConnection(conx)
    
    def handleConnection(self, connection):
        req = connection.makefile("b")
        status = ""
        reqline = req.readline().decode('utf8')
        try:
            method, url, version = reqline.split(" ", 2)
            assert method in ["POST"]
        except Exception:
            response = "HTTP/1.0 405 Method Not Allowed\r\n\r\n"
            connection.send(response.encode("utf8"))
            connection.close()
            print("NO METHOD FOUND")
            return 
        
        headers = {}
        for line in req:
            line = line.decode("utf8")
            if line == "\r\n": break
            header, value = line.split(":", 1)
            headers[header.lower()] = value.strip()
        
        if 'content-length' in headers:
            length = int(headers['content-length'])
            body = req.read(length).decode('utf8')
            # print(body)
            status = self.httpTomqtt(url, body) 
        else:
            status = "400 Bad Request"
            body = None
        response = "HTTP/1.0 {}\r\n\r\n".format(status)
        connection.send(response.encode("utf8"))
        connection.close()

    def httpTomqtt(self, url, body):
        status = ""
        if url == "/":
            return "406 Not Acceptable"

        url = url[1:]
        if url in self.TOMQTT:
            self.client.publish(topic=url, payload=body)
            status = "200 OK"
        else:
            status =  "404 Not Found"
        return status

    def mqttTohttp(self, msg):
        url = self.url + "/" + msg.topic
        resp = ""
        obj =""
        try:
            obj = json.loads(msg.payload.decode())
            # obj = ast.literal_eval(msg.payload.decode())
        except ValueError or TypeError or SyntaxError:
            print("Error in MQTTHTTP: Error in payload Format: not Json!\n")
            return
        try:
            resp = requests.post(url, json= obj)
        except:
            print("Error in MQTTHTTP: Error in Post Request")
        if resp:
            print(resp.status_code)
