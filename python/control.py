
import os
import sys
import time
import select
import VL53L0X
import datetime
import datetime
import threading
import subprocess
import configparser
import RPi.GPIO as GPIO

import mqtt_broker
import mqtt_client

signPin = 37
curPath = ""
leptonPath = ""
mqttEnable = False
tof = None

def setup():	
	global conf
	global curPath
	global mqttEnable
	global leptonPath
	
	#GPIO
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(signPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	
	# Envi Path
	curPath, curFile = os.path.split(os.path.abspath(sys.argv[0]))
	leptonPath = "{0}/lepton".format(curPath)
	
	# Config
	conFile = "{0}/Env.conf".format(curPath)
	print(conFile)
	conf = configparser.ConfigParser()
	conf.read(conFile)	
	mqttEnable = bool(conf.get("mqtt_client", "Enable"))
	

def sensor():
	global tof
	global curPath
	global signPin
	global mqttEnable
	global leptonPath
	
	cout = ""
	ir_Reset = True
	ir_Start = False	
	
	mqtt_broker.on_mqtt_connect()
	t = threading.Thread(target = mqtt_broker.on_subscribe)
	t.start()
	print("MQTT Ready..!")	
	print("Waiting...")	
	
	
	# Create a VL53L0X object
	tof = VL53L0X.VL53L0X()

	# Start ranging
	tof.start_ranging(VL53L0X.VL53L0X_BEST_ACCURACY_MODE)

	timing = tof.get_timing()
	if (timing < 20000):
		timing = 20000
	#print ("Timing %d ms" % (timing/1000))
	print("ToF ready..!")
	ir_Reset = True
	
	while True:		
		try:	
			distance = tof.get_distance()	
			#print(distance)		
			if ir_Reset and (distance > 400 and distance <= 600):
				#print ("%d mm" % (distance))	
				ir_Start = True
			else:
				ir_Reset = True
			#ir_Start = True
			if (mqtt_broker.flg_CatchFaceID) or (ir_Start):
				Time1 = datetime.datetime.now() 
				ir_Start = False
				ir_Reset = False				
				mqtt_broker.flg_CatchFaceID = False			
				print("Sensor detect: %d mm" % (distance))
				
				# Subprocess lepton
				cmd = "sudo {0}/raspberrypi_video".format(leptonPath)				
				subprocess.call(cmd, shell = True)	
				
				# Record result
				f = open("{0}/tmpData.txt".format(curPath))
				resultData = f.read().split(',')
				resultData = list(map(float, resultData))
				print("result: {0}\n".format(get_mode(resultData)))
				
				# MQTT Slave
				if mqttEnable:	
					print("mqtt available")				
					print("jetson form:")
					mqtt_client.mqttPub("IR", get_mode(resultData))
					print("MQTT done\n")
				else:
					print("mqtt unavailable")
				
				Time2 = datetime.datetime.now() 				
				print("Time1: {0}".format(Time1))
				print("Time2: {0}".format(Time2))
				print("timespan: {0}\n".format((Time2 - Time1).microseconds))
				
			#if (senIR_S):
				#senStatus = True		
			time.sleep(0.5)											
			
		except KeyboardInterrupt:
			break
		
	GPIO.cleanup()
	print("\n\nGPIO Clean Done..!\n")
	
	tof.stop_ranging()
	print("ToF Done..!")
	
def Average(lst): 
    return (sum(lst) / len(lst))

def get_mode(arr):
    #mode = [];
    arr_appear = dict((a, arr.count(a)) for a in arr);  # 统计各个元素出现的次数
    if max(arr_appear.values()) == 1:  # 如果最大的出现为1
        return;  # 则没有众数
    else:
        for k, v in arr_appear.items():  # 否则，出现次数最大的数字，就是众数
            if v == max(arr_appear.values()):
                #mode.append(k);
                mode = "%.2f" % k
                break
    return mode;

if __name__=='__main__':
	setup()	
	print("Setup ok..!")	
	
	sensor()
