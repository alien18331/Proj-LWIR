
import os
import sys
import time
import configparser
import paho.mqtt.client as mqtt

from uuid import getnode as get_mac

import mqtt_broker

# Config
curPath, curFile = os.path.split(os.path.abspath(sys.argv[0]))

conFile = "{0}/Env.conf".format(curPath)
conf = configparser.ConfigParser()
conf.read(conFile)

# MQTT para
ClientName = "{0}".format(conf.get("mqtt_client", "TopicName"))
MQTTTopicName = "{0}".format(conf.get("mqtt_client", "TopicName"))
ToMQTTTopicServerIP = "{0}".format(conf.get("mqtt_client", "IP"))
ToMQTTTopicServerPort = "{0}".format(conf.get("mqtt_client", "PORT"))

# MQTT para
#ToMQTTTopicServerIP = "10.192.194.34" #"10.192.218.252"
#ToMQTTTopicServerPort = 1883 #port
#MQTTTopicName = "IR" #TOPIC name

mqttc = mqtt.Client(ClientName) 
mqttc.connect(ToMQTTTopicServerIP, int(ToMQTTTopicServerPort))

# jetson para
def get_mac():
    import uuid
    return str(':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])).upper()

def mqttPub(userID, centerTmp = 99):
   global mqttc
   global ClientName
   
   nTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
   #userID = "00048766"
   #centerTmp = 36
   machID = ClientName
   macID = get_mac()

   #jetson-form
   f_JSON = ("{{\n" \
            "    \"createdAt\": \"{0}\",\n" \
   #         "    \"createdAt\": ISODate(\"{0}\"),\n" \
            "    \"data\": {{\n" \
            "        \"userID\": {1},\n" \
            "        \"temp\": {2}\n" \
            "    }},\n" \
            "    \"macAddress\": \"{3}\",\n" \
            "    \"createdBy\": \"{4}\"\n" \
            "}}").format(nTime, mqtt_broker.userID, centerTmp, macID, machID)

   print(f_JSON)   
   mqttc.publish("IR", f_JSON)
   
if __name__=='__main__':	
	mqttPub()
