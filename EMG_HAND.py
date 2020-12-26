import pyglet
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
Fs = 1000
FlexWindowSize = 0.25
data = []
displayData = [-2 for i in range(WindowSize)]
flexing = False
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
    #print ((readMAX1242_spidev()>>2))

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
print('Close Window to exit')

#Load and place image resources
pyglet.resource.path = ['./Resources']
pyglet.resource.reindex()
ForeArm_image = pyglet.resource.image("forearm.png")
Bicep_image = pyglet.resource.image("Bicep.png")
ForeArm_image.anchor_x = 7
ForeArm_image.anchor_y = ForeArm_image.height-150
Bicep_image.anchor_x = Bicep_image.width/2
Bicep_image.anchor_y = Bicep_image.height/2

#Define the moving ForeArm class
class ForeArm(pyglet.sprite.Sprite):
  def __init__(self, *args, **kwargs):
    super(ForeArm,self).__init__(img=ForeArm_image,*args, **kwargs)	
    self.rotate_speed = 100.0
    self.rotation_upper_limit = -10
    self.rotation_lower_limit = -100
    self.rotation = self.rotation_upper_limit
    self.key_handler = pyglet.window.key.KeyStateHandler()

  def update(self, dt):
    if flexing:
      if not ((self.rotation-self.rotate_speed*dt) <=  self.rotation_lower_limit):
        self.rotation -= self.rotate_speed*dt
      else:
        self.rotation = self.rotation_lower_limit
    else:
      if not((self.rotation+self.rotate_speed*dt) >= self.rotation_upper_limit):
        self.rotation += self.rotate_speed*dt
      else:
        self.rotation = self.rotation_upper_limit


#Setup the main window
main_window = pyglet.window.Window(1000,600)
main_batch = pyglet.graphics.Batch()
background = pyglet.graphics.OrderedGroup(0)
foreground = pyglet.graphics.OrderedGroup(1)
bicep = pyglet.sprite.Sprite(img=Bicep_image,x=350,y=150,batch=main_batch,group=background)
forearm = ForeArm(x=510, y=115,batch=main_batch,group=foreground)
pyglet.gl.glClearColor(1, 1, 1, 1)
main_window.push_handlers(forearm)
main_window.push_handlers(forearm.key_handler)

from components import Report, Servo, Hand

class Robot:
    def __init__(self):
        report = Report()
        self.servo = Servo(report)

        config = {
            'report': report,
            'servo': self.servo,
        }

        self.hand = Hand(config)


    def flex(self):
        # self.hand.close()
        self.servo.move_servo_to_percent(self.hand.channels['thumb'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['index'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['middle'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['ring'], 50)
        self.servo.move_servo_to_percent(self.hand.channels['little'], 0)
        for i in range(5):
            self.servo.sleep(i)
            time.sleep(1)

# invoke a new robot
robot = Robot()

def update(dt):
  global displayData, data, flexing, robot

  newData = list(data)
  data = []
  newDisplay = list(displayData[len(newData):len(displayData)] + newData)
  displayData = list(newDisplay)
  #print max(newData)

  #Put your flex algorithm code here!
  #If flexing is detected, set the 'flexing' variable to True.
  #Otherwise, set it to False.
  if max(newData)>170:
      flexing = True
      robot.hand.close()
  else:
      flexing = False
      robot.hand.open()
  forearm.update(dt)

#Start a new thread to update the plot with acquired data
ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init, interval=25, blit=True)

#Start a new thread to listen for data over UDP
thread = threading.Thread(target=plt.show())
thread.daemon = True
thread.start()

@main_window.event
def on_draw():
    main_window.clear()
    main_batch.draw()

pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()
