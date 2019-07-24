import time
import paho.mqtt.client as mqtt

from uuid import getnode as get_mac

# MQTT para
mqttc = mqtt.Client("IR_Sensor")
ToMQTTTopicServerIP = "10.192.194.34" #"10.192.218.252"
ToMQTTTopicServerPort = 1883 #port
MQTTTopicName = "IR" #TOPIC name

mqttc.connect(ToMQTTTopicServerIP, ToMQTTTopicServerPort)

mqttc.publish(MQTTTopicName, "11111111")
