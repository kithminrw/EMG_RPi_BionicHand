#!/usr/bin/python

import time, signal, sys
from time import sleep
from navio.adafruit_ads1x15 import ADS1x15
import navio.util
import RPi.GPIO as GPIO

navio.util.check_apm()

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
#print 'Press Ctrl+C to exit'


#Define number of PoE plugs
plugs = 3

# Number of channels are 2*plugs, voltage and current measurements
n_channels = plugs * 2

#Define Multiplexer ctrl GPIOs
s0 = 16
s1 = 19
s2 = 26
s3 = 20

ADS1015 = 0x00  # 12-bit ADC
ADS1115 = 0x01	# 16-bit ADC

# Select the gain
gain = 6144  # +/- 6.144V
# gain = 4096  # +/- 4.096V
# gain = 2048  # +/- 2.048V
# gain = 1024  # +/- 1.024V
# gain = 512   # +/- 0.512V
# gain = 256   # +/- 0.256V

# Select the sample rate
# sps = 8    # 8 samples per second
# sps = 16   # 16 samples per second
# sps = 32   # 32 samples per second
# sps = 64   # 64 samples per second
# sps = 128  # 128 samples per second
sps = 250  # 250 samples per second
# sps = 475  # 475 samples per second
# sps = 860  # 860 samples per second

# Initialise the ADC using the default mode (use default I2C address)
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
adc = ADS1x15(ic=ADS1115)

#Pin Setup:
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(s0, GPIO.OUT) # set pin as output
GPIO.setup(s1, GPIO.OUT) # set pin as output
GPIO.setup(s2, GPIO.OUT) # set pin as output
GPIO.setup(s3, GPIO.OUT) # set pin as output

#Select 0 channel of Multiplexer as default
GPIO.output(s0, GPIO.LOW)
GPIO.output(s1, GPIO.LOW)
GPIO.output(s2, GPIO.LOW)
GPIO.output(s3, GPIO.LOW)

#initialize
i =0

while 1:
#	if i == 1:
#		# Switch to ch0
#		GPIO.output(s0, GPIO.LOW)
#		i =0
#		# Reading all channels
#		volts = adc.readADCSingleEnded(0, gain, sps) / 1000
#		print "Vin: %.4fV " % (volts)
#		print "PoE Volts: %.4fV \t |" % (volts*11)		
#	else :
#		# Switch to ch1
#		GPIO.output(s0, GPIO.HIGH)
#		i =1
#		# Reading all channels
#		volts = adc.readADCSingleEnded(0, gain, sps) / 1000
#		print "Va: %.4fV " % (volts)
#		print "Current Consumed: %.4fA |\n" % (volts/0.7)			



        print ('------------')
	print ('| DEVICE 1 |')
	print ('------------')

        # Switch to ch0
	GPIO.output(s0, GPIO.LOW)
	GPIO.output(s1, GPIO.LOW)
        GPIO.output(s2, GPIO.LOW)
        sleep (1)
	# Reading all channels
	volts = adc.readADCSingleEnded(0, gain, sps) / 1000
	#print "Vin: %.4fV " % (volts)
	print "Vin: %.4fV " % (volts- 0.0009)
        #print "PoE Volts: %.4fV \t |" % (volts*11)	
	print "PoE Volts: %.4fV \t |" % ((volts-0.0009)*10.965)
        
        # Switch to ch1
        GPIO.output(s0, GPIO.HIGH)
        GPIO.output(s1, GPIO.LOW)
	sleep (1)
	# Reading all channels
	volts = adc.readADCSingleEnded(0, gain, sps) / 1000
	print "Va: %.4fV " % (volts-0.0013)
	print "Current Consumed: %.4fA |\n" % ((volts-0.0013)/(10*0.3))

        sleep (1)


        print ('------------')
        print ('| DEVICE 2 |')
        print ('------------')

        # Switch to ch2
        GPIO.output(s0, GPIO.LOW)
        GPIO.output(s1, GPIO.HIGH)
        sleep (1)        
	# Reading all channels
        volts = adc.readADCSingleEnded(0, gain, sps) / 1000
        print "Vin: %.4fV " % (volts- 0.0009)
        print "PoE Volts: %.4fV \t |" % (volts*11)


        # Switch to ch3
        GPIO.output(s0, GPIO.HIGH)
        GPIO.output(s1, GPIO.HIGH)
        sleep (1)
        # Reading all channels
        volts = adc.readADCSingleEnded(0, gain, sps) / 1000
        print "Va: %.4fV " % (volts)
        print "Current Consumed: %.4fA |\n" % (volts/(10*0.3))

        sleep (1)


        print ('------------')
        print ('| DEVICE 3 |')
        print ('------------')

        # Switch to ch4
        GPIO.output(s0, GPIO.LOW)
        GPIO.output(s1, GPIO.LOW)
        GPIO.output(s2, GPIO.HIGH)
        sleep (1)
        # Reading all channels
        volts = adc.readADCSingleEnded(0, gain, sps) / 1000
        print "Vin: %.4fV " % (volts)
        print "PoE Volts: %.4fV \t |" % (volts*11)


        # Switch to ch5
        GPIO.output(s0, GPIO.HIGH)
        GPIO.output(s1, GPIO.LOW)
        GPIO.output(s2, GPIO.HIGH)
        sleep (1)
        # Reading all channels
        volts = adc.readADCSingleEnded(0, gain, sps) / 1000
        print "Va: %.4fV " % (volts)
        print "Current Consumed: %.4fA |\n" % (volts/(0.3*10))

	sleep (1)
