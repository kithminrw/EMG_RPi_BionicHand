import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#These are standard python modules
import threading
import time
import os
import sys

#These modules must be installed via apt-get or pip-3.2
os.system('sudo pigpiod')
import RPi.GPIO as GPIO
import pigpio
import spidev

#Un-comment this if using OS-X.
os.system('defaults write org.python.python ApplePersistenceIgnoreState NO')

WindowSize = 5000
SampleRate = 1000.0
VoltsPerBit = 2.5/256

#Define global variables
data = []
displayData = [-2 for i in range(WindowSize)]
SPI_CE0 = 8
PWM_Pin = 4
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
    #print (sample)
    return sample

def GetSample_CBF(gpio, level, tick):
    global data
    data.append(readMAX1242_spidev()>>2)
    print ((readMAX1242_spidev()>>2))

#Set the PWM pin to oscillate at a frequency equal to 1 kHz with a 50% duty cycle
pi.set_PWM_dutycycle(PWM_Pin, 128)
pi.set_PWM_frequency(PWM_Pin,1000)

#Initialize the callback functions for acquiring samples and sending data
GetSample_callback = pi.callback(PWM_Pin, pigpio.RISING_EDGE, GetSample_CBF)

#Setup plot parameters
fig, ax = plt.subplots()
line, = ax.plot([], '-r') #red line, no points
plt.xlim([0,WindowSize/SampleRate])
plt.ylim([-VoltsPerBit*128,VoltsPerBit*128]) #samples will vary from 0 to 255
plt.xlabel('Time (Seconds)')
plt.ylabel('EMG (mV)')

#This function updates what data is displayed. It will be called in a separate thread created by the animation.FuncAnimation command
def animate(i):
  global displayData, data

  newData = list(data)
  data = []
  newDisplay = list(displayData[len(newData):len(displayData)] + newData)
  displayData = list(newDisplay)
  line.set_ydata([i*VoltsPerBit-1.25 for i in displayData])
  line.set_color('blue')
  return line,

#Init only required for blitting to give a clean slate.
def init():
  line.set_xdata([i/SampleRate for i in range(WindowSize)])
  line.set_ydata([i for i in displayData])
  return line,

print('Connected')
print("Listening for incoming messages...")
print('Close Plot Window to exit')

#Start a new thread to listen for data over UDP
#thread = threading.Thread(target=data_listener)
#thread.daemon = True
#thread.start()

#Start a new thread to update the plot with acquired data
ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init, interval=25, blit=True)

#Show the plot
plt.show()
