#These are standard python modules
import socket
import time
import os
import sys

#These modules must be installed via apt-get or pip-3.2
os.system('sudo pigpiod')
import RPi.GPIO as GPIO
import pigpio
import spidev

#Define globals
SPI_CE0 = 8
PWM_Pin = 4
UDP_Buffer = []
pi = pigpio.pi()
spi = spidev.SpiDev()

#Disable GPIO warnings
GPIO.setwarnings(False)

#This function cleans up IO accesss and should be called right before the program exits
def cleanUpGPIOs():
    pi.set_PWM_dutycycle(4,0)
    pi.stop()
    os.system('sudo killall pigpiod')
    GPIO.cleanup()

#Handle command line arguments
if (len(sys.argv) == 2):
    try:
        UDP_IP = sys.argv[1]
        socket.inet_aton(UDP_IP)
    except:
        cleanUpGPIOs()
        sys.exit('Invalid IP address, Try again')
else:
    cleanUpGPIOs()
    sys.exit('EMG_Acquire <Target IP Address>')

UDP_PORT = 9000
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

#sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

#Setup SPI_CE0 to be an output pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(SPI_CE0, GPIO.OUT)

#Open up the SPI port
spi.open(0,1) #use CE1 so we can manually control CE0

#This function reads a sample from the MAX1242 ADC
def readMAX1242_spidev():
    #Create a falling edge of CE0
    GPIO.output(SPI_CE0, True)
    GPIO.output(SPI_CE0, False)
    
    #Should wait for the data pin to go high before clocking. skip for now because the GPIO updating is slow enought that we don't need to wait.
    resp = spi.xfer2([0,0])
    GPIO.output(SPI_CE0, True)
    
    sample = ((resp[0]&0x7F)<<3) + (resp[1]>>5)
    return sample

#This is a callback function that kicks off a UDP transfer of data
def SendData_CBF(gpio, level, tick):
    global UDP_Buffer, sock
    if (len(UDP_Buffer) > 10):
        BufferToSend = list(UDP_Buffer)
        UDP_Buffer = []
        sock.sendto(bytes(BufferToSend), (UDP_IP, UDP_PORT))

#This is a callback function that kicks off an ADC sample
def GetSample_CBF(gpio, level, tick):
    UDP_Buffer.append(readMAX1242_spidev()>>2)

#Set the PWM pin to oscillate at a frequency equal to 1 kHz with a 50% duty cycle
pi.set_PWM_dutycycle(PWM_Pin, 128)
pi.set_PWM_frequency(PWM_Pin,1000)

#Initialize the callback functions for acquiring samples and sending data
GetSample_callback = pi.callback(PWM_Pin, pigpio.RISING_EDGE, GetSample_CBF)
SendData_callback = pi.callback(SPI_CE0, pigpio.RISING_EDGE, SendData_CBF)

#Put the main process in a sleep loop
try:
    print('Data is streaming to ' + str(UDP_IP))
    print('Press ctrl-C to stop')
    while (True):
        time.sleep(10)
except:
    print('\nUser Terminated the program!\n')

finally:
    cleanUpGPIOs()
