import paho.mqtt.client as mqtt
import json


MQTT_HOST = "dashboard.lp.smsy.haw-hamburg.de"#"broker.hivemq.com"
MQTT_PORT = 1901#1883


def on_message(client, userdata, msg):
    str = msg.payload.decode()
    dic = json.loads(str)
    code = dic["doorCode"]
    backupCode = dic["backupCode"]
    email = dic["email"]

    print("Tuercode ist: {}\nBackupCode ist: {}\nEmail ist: {}".format(code, backupCode, email))

client = mqtt.Client()
client.connect(MQTT_HOST, MQTT_PORT, 60)

client.subscribe("signal/setTuerCode", qos=2)
client.subscribe("door/code", qos=2)

#client.publish(topic="signal/getTuerCode",qos=2)
client.publish(topic="door/getcode", payload= "{\"email\":\"maxMustermann@mail.com\"}", qos=2)
#client.publish(topic="lp/flur/schloss/set", payload="0", qos=2)
client.on_message = on_message
#client.publish(topic="signal/setTuercodeManuell", payload="{\"code\": \"30\", \"backupCode\": \"865\"}", qos=2)


client.loop_forever()