
import socket
import paho.mqtt.client as mqtt

myname = socket.getfqdn(socket.gethostname(  ))
myaddr = socket.gethostbyname(myname)

MQTTHOST = str(myaddr)
mqttClient = mqtt.Client()

flg_CatchFaceID = False
userID = ""

# 连接MQTT服务器
def on_mqtt_connect(MQTTPORT = 1883):
    mqttClient.connect(MQTTHOST, MQTTPORT)
    mqttClient.loop_start()

# publish 消息
def on_publish(topic, payload, qos):
    mqttClient.publish(topic, payload, qos)

# 消息处理函数
def on_message_come(lient, userdata, msg):
    global tmpflg
    global userID
    
    userID = str(msg.payload.decode("utf-8"))
    print("{0}".format(userID))
    flg_CatchFaceID = True

# subscribe 消息
def on_subscribe():
    mqttClient.subscribe("FaceID", 1)
    mqttClient.on_message = on_message_come # 消息到来处理函数
    
def main():
    global tmpflg
        
    on_mqtt_connect()
    on_subscribe()
    
    #on_publish("IR", "Hello Python!", 1)
    
    while True:   
        pass

if __name__ == '__main__':
    main()
