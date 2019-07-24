
import sys
import time
import select
import RPi.GPIO as GPIO

signPin = 37

def setup():	
		
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(signPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def sensor():
	global signPin
	senStatus = False 
	
	print("Waiting..")	
	while True:	
		try:		
			if not (GPIO.input(signPin)): # Detect
				senStatus = True
			
			while senStatus :	
				print("Sensor detect..!")
				time.sleep(1)
				
				if (GPIO.input(signPin)):
					print("Waiting..")
					senStatus = False
					break
							
		except KeyboardInterrupt:
			break
		
	GPIO.cleanup()
	print("\nGPIO Clean Done..!")

if __name__=='__main__':
	setup()	
	print("setup done !")	
	
	sensor()
