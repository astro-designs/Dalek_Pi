#!/usr/bin/env python2.7
# @Dalek_Pi

# Motor Control
# Camera
# Line-follower
# YouTube channel
# Wireless PS3 controller interface

# Uses the PiZ-Moto motor driver board

import dalek_pi_config as dalek_pi
import dalek_pi_auth
import tweepy
from tweepy.api import API
import RPi.GPIO as GPIO
import pygame
import time
import os
import sys
import subprocess
import Tkinter
import wiringpi as wiringpi
from datetime import datetime

API_KEY = dalek_pi_auth.API_KEY
API_SECRET = dalek_pi_auth.API_SECRET
ACCESS_TOKEN = dalek_pi_auth.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = dalek_pi_auth.ACCESS_TOKEN_SECRET

key = tweepy.OAuthHandler(API_KEY, API_SECRET)
key.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(key)

TweetOn = dalek_pi.TweetOn
DebugOn = dalek_pi.DebugOn
CameraOn = dalek_pi.DebugOn
DriveOn = dalek_pi.DriveOn
VoiceOn = dalek_pi.VoiceOn

# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define which GPIO pins are used to control the voice box
pinDalekSpeak1 = 22
pinDalekSpeak2 = 23
pinDalekSpeak3 = 27
pinDalekSpeak4 = 24
pinDalekSpeak5 = 11

# Set variables for the GPIO motor pins
pinMotorAForwards = 10
pinMotorABackwards = 9
pinMotorBForwards = 7
pinMotorBBackwards = 8

# Options to switch motors around...
# In case wires get swapped...
# Work in progress, not yet working
SwapMotors = False
ReverseLeftMotor = False
ReverseRightMotor = False

# Set variables for the line detector GPIO pin
pinLineFollower = 25

# Define GPIO pins to use on the Pi
pinTrigger = 17
pinEcho = 18

# Set variable for the LED pins
pinLED1 = 5
pinLED2 = 6

# Define the PWM / Servo pins (these are fixed!)
pinServo1 = 12
pinServo2 = 19

# Define the initial pulse-widths for servo positions
DC_forwards = 11
DC_backwards = 20
DC_right = 17
DC_left = 13
DC_Stop = 15

# How many times to turn the pin on and off each second
Frequency = 50
# How long the pin stays on each cycle, as a percent
DutyCycleA = 100
DutyCycleB = 100
# Setting the duty cycle to 0 means the motors will not turn
Stop = 0

# Define a global variable to define a slower speed for turning
TurnDC = 0.5

# Define a global variable to control limit initial acceleration
SpeedRamp = 0.5

# Set the GPIO Pin mode for the VoiceBox controls to be Output
GPIO.setup(pinDalekSpeak1, GPIO.OUT)
GPIO.setup(pinDalekSpeak2, GPIO.OUT)
GPIO.setup(pinDalekSpeak3, GPIO.OUT)
GPIO.setup(pinDalekSpeak4, GPIO.OUT)
GPIO.setup(pinDalekSpeak5, GPIO.OUT)

# Set the GPIO Pin mode for the motor controls to be Output
GPIO.setup(pinMotorAForwards, GPIO.OUT)
GPIO.setup(pinMotorABackwards, GPIO.OUT)
GPIO.setup(pinMotorBForwards, GPIO.OUT)
GPIO.setup(pinMotorBBackwards, GPIO.OUT)

# Set the GPIO Pin mode for the LED controls to be Output
GPIO.setup(pinLED1, GPIO.OUT)
GPIO.setup(pinLED2, GPIO.OUT)

# Set the pinLineFollower pin as an input so its value can be read
GPIO.setup(pinLineFollower, GPIO.IN)

interval = 0.00                         # Time between keyboard updates in seconds, smaller responds faster but uses more processor time

# Setup pygame and key states
global hadEvent
global LeftStickUp
global LeftStickDown
global LeftStickLeft
global LeftStickRight
global RightStickUp
global RightStickDown
global RightStickLeft
global RightStickRight
global HatStickUp
global HatStickDown
global HatStickLeft
global HatStickRight
global TriangleButton
global SquareButton
global CircleButton
global XButton
global HomeButton
global StartButton
global SelectButton
global YButton
global AButton
global BButton
global R1Button
global R2Button
global R3Button
global L1Button
global L2Button
global L3Button
global moveQuit
hadEvent = True
LeftStickUp = False
LeftStickDown = False
LeftStickLeft = False
LeftStickRight = False
RightStickUp = False
RightStickDown = False
RightStickLeft = False
RightStickRight = False
HatStickUp = False
HatStickDown = False
HatStickLeft = False
HatStickRight = False
TriangleButton = False
SquareButton = False
CircleButton = False
XButton = False
YButton = False
AButton = False
BButton = False
HomeButton = False
StartButton = False
SelectButton = False
R1Button = False
R2Button = False
R3Button = False
L1Button = False
L2Button = False
L3Button = False
moveQuit = False

global stick
stick = "Left"

# Flash the LEDs
def FlashLEDs(flashes = 1, delay = 0.25):

    for flash in range(0, flashes):
        GPIO.output(pinLED1, True)
        GPIO.output(pinLED2, True)
        time.sleep(delay)
        GPIO.output(pinLED1, False)
        GPIO.output(pinLED2, False)
        time.sleep(delay)



# Needed to allow PyGame to work without a monitor
os.environ["SDL_VIDEODRIVER"]= "dummy"

#Initialise pygame & controller(s)
pygame.init()
print 'Waiting for joystick... (press CTRL+C to abort)'
while True:
    try:
        try:
            pygame.joystick.init()
            # Attempt to setup the joystick
            if pygame.joystick.get_count() < 1:
                # No joystick attached, toggle the LED
                #ZB.SetLed(not ZB.GetLed())
                pygame.joystick.quit()
                time.sleep(0.1)
            else:
                # We have a joystick, attempt to initialise it!
                joystick = pygame.joystick.Joystick(0)
                break
        except pygame.error:
            # Failed to connect to the joystick, toggle the LED
            #ZB.SetLed(not ZB.GetLed())
            pygame.joystick.quit()
            time.sleep(0.1)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print '\nUser aborted'
        #ZB.SetLed(True)
        sys.exit()
print 'Joystick found'
joystick.init()

print 'Initialised Joystick : %s' % joystick.get_name()

if "Rock Candy" in joystick.get_name():
    FlashLEDs(2,0.5)
    print ("Found Rock Candy Wireless PS3 controller")
    # pygame controller constants (Rock Candy Controller)
    JoyButton_Square = 0
    JoyButton_X = 1
    JoyButton_Circle = 2
    JoyButton_Triangle = 3
    JoyButton_L1 = 4
    JoyButton_R1 = 5
    JoyButton_L2 = 6
    JoyButton_R2 = 7
    JoyButton_Select = 8
    JoyButton_Start = 9
    JoyButton_L3 = 10
    JoyButton_R3 = 11
    JoyButton_Home = 12
    axisUpDown = 1                          # Joystick axis to read for up / down position
    RightaxisUpDown = 3                     # Joystick axis to read for up / down position
    axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
    axisLeftRight = 0                       # Joystick axis to read for left / right position
    RightaxisLeftRight = 2                  # Joystick axis to read for left / right position
    axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
    # These buttons do not exist for this controller...
    # So map to compatible positions
    JoyButton_A = 999                       # Not supported on this controller
    JoyButton_B = 999                       # Not supported on this controller
    JoyButton_Y = 999                       # Not supported on this controller
else:
    FlashLEDs(3,0.5)
    print (" The other cheap Wireless PS3 controller")
    # pygame controller constants (ShanWan PC/PS3/Android)
    JoyButton_A = 0
    JoyButton_B = 1
    JoyButton_X = 3
    JoyButton_Y = 4
    JoyButton_R1 = 7
    JoyButton_L1 = 6
    JoyButton_R2 = 9
    JoyButton_L2 = 8
    JoyButton_Select = 10
    JoyButton_Start = 11
    JoyButton_L3 = 13
    JoyButton_R3 = 14
    axisUpDown = 1                          # Joystick axis to read for up / down position
    RightaxisUpDown = 3                     # Joystick axis to read for up / down position
    axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
    axisLeftRight = 0                       # Joystick axis to read for left / right position
    RightaxisLeftRight = 2                  # Joystick axis to read for left / right position
    axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
    # These buttons do not exist for this controller...
    JoyButton_Square = 999                  # Not supported on this controller
    JoyButton_Circle = 999                  # Not supported on this controller
    JoyButton_Triangle = 999                # Not supported on this controller
    JoyButton_Home = 999                    # Not supported on this controller


# Check number of joysticks in use...
joystick_count = pygame.joystick.get_count()
print("joystick_count")
print(joystick_count)
print("--------------")

# Check number of axes on joystick...
numaxes = joystick.get_numaxes()
print("numaxes")
print(numaxes)
print("--------------")

# Check number of buttons on joystick...
numbuttons = joystick.get_numbuttons()
print("numbuttons")
print(numbuttons)

# Pause for a moment...
time.sleep(2)


# Turn all motors off
def StopMotors():
    global SpeedRamp

    SpeedRamp = 0.5

    pwmMotorAForwards.ChangeDutyCycle(Stop)
    pwmMotorABackwards.ChangeDutyCycle(Stop)
    pwmMotorBForwards.ChangeDutyCycle(Stop)
    pwmMotorBBackwards.ChangeDutyCycle(Stop)

    
# Turn both motors backwards
def Backwards():
    pwmMotorAForwards.ChangeDutyCycle(DutyCycleA)
    pwmMotorABackwards.ChangeDutyCycle(Stop)
    pwmMotorBForwards.ChangeDutyCycle(DutyCycleB)
    pwmMotorBBackwards.ChangeDutyCycle(Stop)


# Turn both motors forwards
def Forwards():
    pwmMotorAForwards.ChangeDutyCycle(Stop)
    pwmMotorABackwards.ChangeDutyCycle(DutyCycleA)
    pwmMotorBForwards.ChangeDutyCycle(Stop)
    pwmMotorBBackwards.ChangeDutyCycle(DutyCycleB)


# Turn Right
def Right():
    global TurnDC
    
    #print("Right")
    pwmMotorAForwards.ChangeDutyCycle(Stop)
    pwmMotorABackwards.ChangeDutyCycle(DutyCycleA * TurnDC)
    pwmMotorBForwards.ChangeDutyCycle(DutyCycleB * TurnDC)
    pwmMotorBBackwards.ChangeDutyCycle(Stop)


def BLeft():
    global TurnDC
    
    #print("Right")
    pwmMotorAForwards.ChangeDutyCycle(DutyCycleA * TurnDC)
    pwmMotorABackwards.ChangeDutyCycle(Stop)
    pwmMotorBForwards.ChangeDutyCycle(DutyCycleB)
    pwmMotorBBackwards.ChangeDutyCycle(Stop)


def FLeft():
    global TurnDC
    
    #print("Right")
    pwmMotorAForwards.ChangeDutyCycle(Stop)
    pwmMotorABackwards.ChangeDutyCycle(DutyCycleA * TurnDC)
    pwmMotorBForwards.ChangeDutyCycle(Stop)
    pwmMotorBBackwards.ChangeDutyCycle(DutyCycleB)

# Turn left
def Left():
    global TurnDC
    
    #print("Left")
    pwmMotorAForwards.ChangeDutyCycle(DutyCycleA * TurnDC)
    pwmMotorABackwards.ChangeDutyCycle(Stop)
    pwmMotorBForwards.ChangeDutyCycle(Stop)
    pwmMotorBBackwards.ChangeDutyCycle(DutyCycleB * TurnDC)

def BRight():
    global TurnDC
    
    #print("Left")
    pwmMotorAForwards.ChangeDutyCycle(DutyCycleA)
    pwmMotorABackwards.ChangeDutyCycle(Stop)
    pwmMotorBForwards.ChangeDutyCycle(DutyCycleB * TurnDC)
    pwmMotorBBackwards.ChangeDutyCycle(Stop)

def FRight():
    global TurnDC
    
    #print("Left")
    pwmMotorAForwards.ChangeDutyCycle(Stop)
    pwmMotorABackwards.ChangeDutyCycle(DutyCycleA)
    pwmMotorBForwards.ChangeDutyCycle(Stop)
    pwmMotorBBackwards.ChangeDutyCycle(DutyCycleB * TurnDC)

# Return True if the line detector is over a black line
def IsOverBlack():
    if GPIO.input(pinLineFollower) == 0:
        return True
    else:
        return False

# Search for the black line
def SeekLine():
    print("Seeking the line")
    # The direction the robot will turn - True = Left
    Direction = True
    
    SeekSize = 0.25 # Turn for 0.25s
    SeekCount = 1 # A count of times the robot has looked for the line 
    MaxSeekCount = 5 # The maximum time to seek the line in one direction
    # Turn the robot left and right until it finds the line
    # Or it has been searched for long enough
    while SeekCount <= MaxSeekCount:
        # Set the seek time
        SeekTime = SeekSize * SeekCount
        
        # Start the motors turning in a direction
        if Direction:
            print("Looking left")
            Left()
        else:
            print("Looking Right")
            Right()
        
        # Save the time it is now
        StartTime = time.time()
        
        # While the robot is turning for SeekTime seconds,
        # check to see whether the line detector is over black
        while time.time()-StartTime <= SeekTime:
            if IsOverBlack():
                StopMotors()
                # Exit the SeekLine() function returning
                # True - the line was found
                return True
                
        # The robot has not found the black line yet, so stop
        StopMotors()


        
        # Increase the seek count
        SeekCount += 1
        
        # Change direction
        Direction = not Direction
        
    # The line wasn't found, so return False
    return False


def do_linefollower():
    global SpeedRamp

    #repeat the next indented block forever
    print("Following the line")
    KeepTrying = True
    while KeepTrying == True:
        # If the sensor is Low (=0), it's above the black line
        if IsOverBlack():
            SpeedRamp = SpeedRamp + 0.05
            if SpeedRamp > 1:
                SpeedRamp = 1
            Forwards()
            time.sleep(0.2)
            # If not (else), print the following
        else:
            StopMotors()
            if SeekLine() == False:
                StopMotors()
                print("The robot has lost the line")
                KeepTrying = False
            else:
                print("Following the line")
    print("Exiting the line-following routine")
    StopMotors()


def do_proximity():
    print("Looking for a wall...")
    #Initialise Distance variable for first average calculation
    Distance = 100
    
    # Repeat the next indented block forever
    while Distance > 2.7:

        # Start going forwards...
        Forwards()
    
        # Small delay to ensure read frequency never exceeds 40Hz
        time.sleep(0.025)

        # Send 10us pulse to trigger
        GPIO.output(pinTrigger, True)
        time.sleep(0.00001)
        GPIO.output(pinTrigger, False)
        
        # Start the timer
        StartTime = time.time()
        
        # The start time is reset until the Echo pin is taken high (==1)
        while GPIO.input(pinEcho)==0:
            StartTime = time.time()
        
        # Stop when the Echo pin is no longer high - the end time
        while GPIO.input(pinEcho)==1:
            StopTime = time.time()
            # If the sensor is too close to an object, the Pi cannot
            # see the echo quickly enough, so it has to detect that
            # problem and say what has happened
            if StopTime-StartTime >= 0.04:
                print("Hold on there! You're too close for me to see.")
                StopTime = StartTime
                break
        
        # Remember previous measurement for running average calculation
        OldDistance = Distance

        # Calculate pulse length
        ElapsedTime = StopTime - StartTime
        # Distance pulse travelled in that time is
        # time multiplied by the speed of sound (cm/s)
        Distance = ElapsedTime * 34326
        
        # That was the distance there and back so halve the value
        Distance = Distance / 2
        
        # Calculate running average
        Distance = Distance + OldDistance
        Distance = Distance / 2
        
        print("Distance : %.1f" % Distance)

    # Exit while loop
    StopMotors()

def PygameHandler(events):
    # Variables accessible outside this function
    global hadEvent
    global LeftStickUp
    global LeftStickDown
    global LeftStickLeft
    global LeftStickRight
    global RightStickUp
    global RightStickDown
    global RightStickLeft
    global RightStickRight
    global HatStickUp
    global HatStickDown
    global HatStickLeft
    global HatStickRight
    global TriangleButton
    global SquareButton
    global CircleButton
    global XButton
    global YButton
    global AButton
    global BButton
    global HomeButton
    global StartButton
    global SelectButton
    global R1Button
    global R2Button
    global R3Button
    global L1Button
    global L2Button
    global L3Button
    global moveQuit

    # Handle each event individually
    for event in events:
        #print ("Event: ", event)
        if event.type == pygame.QUIT:
            print ("QUIT")
            # User exit
            hadEvent = True
            moveQuit = True
        elif event.type == pygame.JOYHATMOTION:
            # A key has been pressed, see if it is one we want
            hadEvent = True
            #print ("Hat Motion: ", event.value)
            hat = joystick.get_hat(0)
            # Hat up/down
            if hat[0] == -1:
                HatStickLeft = True
            elif hat[0] == 1:
                HatStickRight = True
            else:
                HatStickLeft = False
                HatStickRight = False
            # Hat left/right
            if hat[1] == -1:
                HatStickDown = True
            elif hat[1] == 1:
                HatStickUp = True
            else:
                HatStickDown = False
                HatStickUp = False
            
        elif event.type == pygame.JOYBUTTONDOWN:
            # A key has been pressed, see if it is one we want
            hadEvent = True
            print ("Button Down: ", event.button)
            if event.button == JoyButton_Square:
                SquareButton = True
            elif event.button == JoyButton_X:
                XButton = True
            elif event.button == JoyButton_Circle:
                CircleButton = True
            elif event.button == JoyButton_Triangle:
                TriangleButton = True
            elif event.button == JoyButton_Y:
                YButton = True
            elif event.button == JoyButton_A:
                AButton = True
            elif event.button == JoyButton_B:
                BButton = True
            elif event.button == JoyButton_L1:
                L1Button = True
            elif event.button == JoyButton_R1:
                R1Button = True
            elif event.button == JoyButton_L2:
                L2Button = True
            elif event.button == JoyButton_R2:
                R2Button = True
            elif event.button == JoyButton_L3:
                L3Button = True
            elif event.button == JoyButton_R3:
                R3Button = True
            elif event.button == JoyButton_Select:
                SelectButton = True
            elif event.button == JoyButton_Start:
                StartButton = True
            elif event.button == JoyButton_Home:
                HomeButton = True
        elif event.type == pygame.JOYBUTTONUP:
            # A key has been released, see if it is one we want
            hadEvent = True
            #print ("Button Up: ", event.button)
            if event.button == JoyButton_Square:
                SquareButton = False
            elif event.button == JoyButton_X:
                XButton = False
            elif event.button == JoyButton_Circle:
                CircleButton = False
            elif event.button == JoyButton_Triangle:
                TriangleButton = False
            elif event.button == JoyButton_Y:
                YButton = False
            elif event.button == JoyButton_A:
                AButton = False
            elif event.button == JoyButton_B:
                BButton = False
            elif event.button == JoyButton_L1:
                L1Button = False
            elif event.button == JoyButton_R1:
                R1Button = False
            elif event.button == JoyButton_L2:
                L2Button = False
            elif event.button == JoyButton_R2:
                R2Button = False
            elif event.button == JoyButton_L3:
                L3Button = False
            elif event.button == JoyButton_R3:
                R3Button = False
            elif event.button == JoyButton_Select:
                SelectButton = False
            elif event.button == JoyButton_Start:
                StartButton = False
            elif event.button == JoyButton_Home:
                HomeButton = False
        elif event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved, read axis positions (-1 to +1)
            hadEvent = True
            upDown = joystick.get_axis(axisUpDown)
            leftRight = joystick.get_axis(axisLeftRight)
            RightUpDown = joystick.get_axis(RightaxisUpDown)
            RightLeftRight = joystick.get_axis(RightaxisLeftRight)
            # Invert any axes which are incorrect
            if axisUpDownInverted:
                upDown = -upDown
            if axisLeftRightInverted:
                leftRight = -leftRight
            # Determine Up / Down values for Left Stick
            if upDown < -0.5:
                print ("LeftStickUp")
                LeftStickUp = True
                LeftStickDown = False
            elif upDown > 0.5:
                print ("LeftStickDown")
                LeftStickUp = False
                LeftStickDown = True
            else:
                LeftStickUp = False
                LeftStickDown = False
            # Determine Up / Down values for Right Stick
            if RightUpDown < -0.5:
                print ("RightStickUp")
                RightStickUp = True
                RightStickDown = False
            elif RightUpDown > 0.5:
                print ("RightStickDown")
                RightStickUp = False
                RightStickDown = True
            else:
                RightStickUp = False
                RightStickDown = False
            # Determine Left / Right values for Left Stick
            if leftRight < -0.5:
                print ("LeftStickLeft")
                LeftStickLeft = True
                LeftStickRight = False
            elif leftRight > 0.5:
                print ("LeftStickRight")
                LeftStickLeft = False
                LeftStickRight = True
            else:
                LeftStickLeft = False
                LeftStickRight = False
            # Determine Left / Right values for Right Stick
            if RightLeftRight < -0.5:
                print ("RightStickLeft")
                RightStickLeft = True
                RightStickRight = False
            elif RightLeftRight > 0.5:
                print ("RightStickRight")
                RightStickLeft = False
                RightStickRight = True
            else:
                RightStickLeft = False
                RightStickRight = False

        
print("Starting PS3Bot - entering control loop...")

# Set the GPIO to software PWM at 'Frequency' Hertz
pwmMotorAForwards = GPIO.PWM(pinMotorAForwards, Frequency)
pwmMotorABackwards = GPIO.PWM(pinMotorABackwards, Frequency)
pwmMotorBForwards = GPIO.PWM(pinMotorBForwards, Frequency)
pwmMotorBBackwards = GPIO.PWM(pinMotorBBackwards, Frequency)

# Start the software PWM with a duty cycle of 0 (i.e. not moving)
pwmMotorAForwards.start(Stop)
pwmMotorABackwards.start(Stop)
pwmMotorBForwards.start(Stop)
pwmMotorBBackwards.start(Stop)

# Set pins as output and input
GPIO.setup(pinTrigger, GPIO.OUT) # Trigger
GPIO.setup(pinEcho, GPIO.IN) # Echo

# Set the LED Pin mode to be Output
GPIO.setup(pinLED1, GPIO.OUT)
GPIO.setup(pinLED2, GPIO.OUT)

# Set trigger to False (Low)
GPIO.output(pinTrigger, False)

# Dalek_Pi Start-up tweet
def dalek_start():
    global screen_name
    if dalek_pi.TweetStart == True:
        i = datetime.now()
        status = dalek_pi.StartTweet + i.strftime('%Y/%m/%d %H:%M:%S')
        if DebugOn: print "Starting up... Tweeting:", status
        if TweetOn: api.update_status(status=status)
    else:
        print "Starting up... (No Tweeting)"

# Dalek_Pi Shut-down tweet
def dalek_stop():
    global screen_name
    if dalek_pi.TweetStop == True:
        i = datetime.now()
        status = dalek_pi.StopTweet + i.strftime('%Y/%m/%d %H:%M:%S') 
        if DebugOn: print "Shutting down... Tweeting:", status
        if TweetOn: api.update_status(status=status)
    else:
        print "Shutting down... (No Tweeting)"


# Tweet handler
class Stream2Screen(tweepy.StreamListener):
    global tweet_rxd
    def __init__(self, api=None):
        self.api = api or API()
        self.n = 0
        self.m = 20

    def on_status(self, status):
        global tweet_rxd, tweet_rxd_data, screen_name, CameraOn, DriveOn, DebugOn
        tweet_rxd = status.text.encode('utf8')
        tweet_rxd = str(tweet_rxd)
        tweet_rxd_sender = tweet_rxd.lstrip('@Dalek_Pi')
        tweet_rxd = tweet_rxd.lstrip('@Dalek_Pi')
        tweet_rxd = tweet_rxd.lstrip('@dalek_pi')
        tweet_rxd = tweet_rxd.lstrip('@Dalek_pi')
        tweet_rxd = tweet_rxd.lstrip('@dalek_Pi')
        tweet_rxd = tweet_rxd.lower()
        tweet_split = tweet_rxd.split()

        tweet_rxd_data = status.user
        tweet_rxd_data = str(tweet_rxd_data)
        get_user()
        
        if DebugOn: print("Sender: "+screen_name+" ("+user_name+")")
        if DebugOn: print("Message:", tweet_rxd)
        if DebugOn: print(tweet_split[0])
    
        # Process movement requests...
        if tweet_split[0] == 'move' and len(tweet_split) == 3:
            if DriveOn == True:
                direction = tweet_split[1]
                duration = float(tweet_split[2]) / 1000.0
                dalek_move(direction, duration)
            else:
                i = datetime.now()
                status = screen_name + ' ' + 'My drive is impared, I cannot move!: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
                if DebugOn: print "Tweeting:", status
                if TweetOn: api.update_status(status=status)
        
        # Process headpiece movement requests...
        elif tweet_split[0] == 'look':
            if DriveOn == True:
                dalek_look()
            else:
                i = datetime.now()
                status = screen_name + ' ' + 'My drive is impared, I cannot move!: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
                if DebugOn: print "Tweeting:", status
                if TweetOn: api.update_status(status=status)
            
        # Process voice-box requests...
        elif tweet_split[0] == 'voice':
            if VoiceOn == True:
                voice = tweet_rxd.lstrip(' ')
                voice = voice.lstrip('voice')
                voice = voice.lstrip(' ')
                voice = voice.split()
                dalek_voice(voice)
            else:
                i = datetime.now()
                status = screen_name + ' ' + 'My voice is impared, I cannot speak!: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
                if DebugOn: print "Tweeting:", status
                if TweetOn: api.update_status(status=status)

            
        # Process speech requests...
        elif tweet_split[0] == 'say': # Speak whatever comes next...
            if VoiceOn == True:
                message = tweet_rxd.lstrip(' say')
                message = message.lstrip(' ')
                dalek_say(message)
            else:
                i = datetime.now()
                status = screen_name + ' ' + 'My voice is impared, I cannot speak!: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
                if DebugOn: print "Tweeting:", status
                if TweetOn: api.update_status(status=status)
            
        # Process help requests...
        elif tweet_split[0] == 'tweet_help':
            i = datetime.now()
            now = i.strftime('%Y%m%d-%H%M%S')
            image_name = 'help.jpg'
            image_path = '/home/pi/' + image_name
            status = screen_name + ' ' + 'Dalek_Pi Help-sheet: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
            if DebugOn: print "testing tweet_help"
            if TweetOn: api.update_with_media(image_path, status=status)
            
        # Process picture requests...
        elif tweet_split[0] == 'tweet_pic':
            i = datetime.now()
            now = i.strftime('%Y%m%d-%H%M%S')
            photo_name = now + '.jpg'
            photo_path = '/home/pi/' + photo_name
            test_photo_name = 'DalekPi-TestImage.jpg'
            test_photo_path = '/home/pi/' + test_photo_name
            if CameraOn == True:
                if DebugOn: print "Taking picture: " + photo_path
                bashCommand = ("raspistill -t 500 -hf -vf -w 1024 -h 768 -o " + photo_path)
                os.system(bashCommand)
                status = screen_name + ' ' + 'Photo auto-tweet from Dalek_Pi: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
            else:
                if DebugOn: print "Camera is off-line. Sending test image"
                # Alternatively, send a test-image... Should probably define a global to enable / disable this...
                status = screen_name + ' ' + 'Sorry, my camera is off-line. I apologise for the inconvenience - Dalek_Pi: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
            print "testing tweet_pic:" + status
            # Check if the file exists before tweeting...
            if os.path.exists(photo_path):
                 if DebugOn: print "Tweeting image:" + photo_path
                 if TweetOn: api.update_with_media(photo_path, status=status)
            elif os.path.exists(test_photo_path):
                 if DebugOn: print "Tweeting test image:" + test_photo_path
                 if TweetOn: api.update_with_media(test_photo_path, status=status)
        
        # Process request to start line-follower function
        elif tweet_split[0] == 'start_linefollow': # Start line-follower mode. May need to lock-out any other commands if this is running in the background
            bashCommand = ("pio spi-set 0x07 0")
            os.system(bashCommand)
            bashCommand = ("pio dalek-linefollower 1&")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
        elif tweet_split[0] == 'stop_linefollow':
            bashCommand = ("pio spi-set 0x07 1")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
        
        elif tweet_split[0] == 'say_exterminate':
            bashCommand = ("sudo ./text2speech.sh Exterminayte!")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
        
        # Process restricted commands...
        elif tweet_split[0] == 'Debug_On' and screen_name == "@AstroDesignsLtd":
            if DebugOn: print "Turning on debug"
            DebugOn = True
        elif tweet_split[0] == 'Debug_Off' and screen_name == "@AstroDesignsLtd":
            if DebugOn: print "Turning off debug"
            DebugOn = False
        elif tweet_split[0] == 'Drive_On' and screen_name == "@AstroDesignsLtd":
            if DebugOn: print "Turning on drive"
            DriveOn = True
        elif tweet_split[0] == 'Drive_Off' and screen_name == "@AstroDesignsLtd":
            if DebugOn: print "Turning off drive"
            if DebugOn: DriveOn = False
        elif tweet_split[0] == 'Camera_On' and screen_name == "@AstroDesignsLtd":
            if DebugOn: print "Turning camera on"
            CameraOn = True
        elif tweet_split[0] == 'Camera_Off' and screen_name == "@AstroDesignsLtd":
            if DebugOn: print "Turning camera off"
            CameraOn = False
        elif tweet_split[0] == 'exit' and screen_name == "@AstroDesignsLtd":
            dalek_stop()
            if DebugOn: print "Exit command received & understood. Bye!"
            #os._exit
            raise SystemExit
        elif tweet_split[0] == 'reboot' and screen_name == "@AstroDesignsLtd":
            dalek_stop()
            bashCommand = ("sudo ./text2speech.sh Rebooting! Back in a jiffy")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
            bashCommand = ("reboot")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
        elif tweet_split[0] == 'halt' and screen_name == "@AstroDesignsLtd":
            dalek_stop()
            bashCommand = ("sudo ./text2speech.sh Shutting down. Goodbye!")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
            bashCommand = ("halt")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
        elif tweet_split[0] == 'Shutdown' and screen_name == "@AstroDesignsLtd":
            dalek_stop()
            bashCommand = ("sudo ./text2speech.sh Shutting down. Goodbye!")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
            bashCommand = ("shutdown")
            if DebugOn: print "echo:"+bashCommand
            os.system(bashCommand)
        else:
            if DebugOn: print "Command not recognised"
            if DebugOn: print "Command: ", "\"", tweet_split[0], "\""
            if DebugOn: print "Screen Name: ", screen_name
            self.n = self.n+1
            if self.n < self.m: return True
            else:
                if DebugOn: print 'tweets = '+str(self.n)
                return False

# Identify user (screen name & user name) from incoming tweet
def get_user():
    global tweet_rxd_data, user_name, screen_name
    name_index = tweet_rxd_data.find("u'screen_name': u'")
    count = 18
    screen_name = ""
    pos = name_index+count
    for each in range(pos,len(tweet_rxd_data)):
        pos_let = tweet_rxd_data[each]
        if ord(pos_let) <> 39:
            screen_name = screen_name+pos_let
            count +=1
        elif ord(pos_let) == 39: break
    screen_name = "@"+screen_name
    name_index = tweet_rxd_data.find("u'name': u'")
    count = 11
    user_name = ""
    letter = tweet_rxd_data[name_index+count]
    pos = name_index+count
    for each in range(pos,len(tweet_rxd_data)):
        pos_let = tweet_rxd_data[each]
        if ord(pos_let) <> 39:
            user_name = user_name+pos_let
            count +=1
        elif ord(pos_let) == 39: break
    if DebugOn: print "New tweet from: "+screen_name+" ("+user_name+")"
    return


# Tweet to speak function 1
# Raspberry Pi generated voice
def dalek_say(message = ""):
    if DebugOn: print "Dalek_Speak: ",message
    command = 'sudo echo '+message + ' | festival --tts'
    bashCommand = (str(command))
    if DebugOn: print "echo:"+bashCommand
    os.system(bashCommand)


# Tweet to speak function 2
# Controls the pre-recorded voice functions from the Dalek voice-box
def dalek_voice(voice):
    if DebugOn: print "voice:",voice
    if voice == "1":
        GPIO.output(pinDalekSpeak1, True)
    elif voice == "2":
        GPIO.output(pinDalekSpeak2, True)
    elif voice == "3":
        GPIO.output(pinDalekSpeak3, True)
    elif voice == "4":
        GPIO.output(pinDalekSpeak4, True)
    elif voice == "5":
        GPIO.output(pinDalekSpeak5, True)
    else:
        print "Command not recognised"

    time.sleep(0.001)
    GPIO.output(pinDalekSpeak1, False)
    GPIO.output(pinDalekSpeak2, False)
    GPIO.output(pinDalekSpeak3, False)
    GPIO.output(pinDalekSpeak4, False)
    GPIO.output(pinDalekSpeak5, False)
    
    return
    

# Dalek head movement functions
def dalek_look():
    global tweet_rxd
    tweet_rxd = tweet_rxd.lstrip(' ')
    look_cmd = tweet_rxd.lstrip('look')
    look_cmd = look_cmd.lstrip(' ')
    look_cmd_split = look_cmd.split()
    if DebugOn: print "look_cmd_split:",look_cmd_split
    if look_cmd_split[0] == "left":
        wiringpi.pwmWrite(pinServo1,LookLeft)
    elif look_cmd_split[0] == "right":
        wiringpi.pwmWrite(pinServo1,LookRight)
    elif look_cmd_split[0] == "forwards":
        wiringpi.pwmWrite(pinServo1,LookForwards)
    elif look_cmd_split[0] == "up":
        wiringpi.pwmWrite(pinServo2,LookUp)
    elif look_cmd_split[0] == "down":
        wiringpi.pwmWrite(pinServo2,LookDown)
    elif look_cmd_split[0] == "straight":
        wiringpi.pwmWrite(pinServo2,LookStraight)
        wiringpi.pwmWrite(pinServo1,LookForwards)
    else:
        print "Command not recognised"
    return

 
#Dalek motor functions
def dalek_move(direction = "stop", duration = 0):
    if DebugOn: print("Direction",direction)
    if DebugOn: print("Duration",duration)
    if direction == "left":
        if DebugOn: print ("Turning left...")
        Left()
    elif direction == "right":
        if DebugOn: print ("Turning right...")
        Right()
    elif direction == "back":
        if DebugOn: print ("Driving backwards...")
        Backwards()
    elif direction == "backwards":
        if DebugOn: print ("Driving backwards...")
        Backwards()
    elif direction == "forward":
        if DebugOn: print ("Driving forwards...")
        Forwards()
    elif direction == "forwards":
        if DebugOn: print ("Driving forwards...")
        Forwards()
    elif direction == "stop":
        if DebugOn: print ("Stopping...")
        StopMotors()
    else:
        if DebugOn: print "Command not recognised"
        if DebugOn: print ("Stopping...")
        StopMotors()

    time.sleep(duration)
    StopMotors()

# Allow module to settle
time.sleep(0.5)

try:

    if DebugOn: print 'Press Ctrl-C to quit'

    # Start-up tweet
    dalek_start()

    #stream = tweepy.streaming.Stream(key, Stream2Screen())
    #stream.filter(follow=['3997839202'], languages=['en'])

    
    # Loop indefinitely
    while True:
        # Get the currently pressed keys on the keyboard
        PygameHandler(pygame.event.get())
        if hadEvent:
            # Keys have changed, generate the command list based on keys
            hadEvent = False
            if moveQuit:
                break
            elif SelectButton and CircleButton: # Shutdown
                if DebugOn: print ("Halting Raspberry Pi...")
                GPIO.cleanup()
                bashCommand = ("sudo halt")
                os.system(bashCommand)
                break
            elif SelectButton and BButton: # Shutdown
                if DebugOn: print ("Halting Raspberry Pi...")
                GPIO.cleanup()
                bashCommand = ("sudo halt")
                os.system(bashCommand)
                break
            elif SelectButton and TriangleButton: # Reboot
                print ("Rebooting Raspberry Pi...")
                GPIO.cleanup()
                bashCommand = ("sudo reboot now")
                os.system(bashCommand)
                break
            elif SelectButton and YButton: # Reboot
                if DebugOn: print ("Rebooting Raspberry Pi...")
                GPIO.cleanup()
                bashCommand = ("sudo reboot now")
                os.system(bashCommand)
                break
            elif SelectButton and XButton: # Exit
                if DebugOn: print ("Exiting program...")
                break
            elif StartButton and CircleButton: 
                print ("Start Line-follower")
                #do_linefollower()
            elif StartButton and SquareButton: 
                if DebugOn: print ("Start Proximity")
                #do_proximity()
            elif StartButton and XButton: 
                if DebugOn: print ("Start Avoidance")
                #do_proximity()
            elif StartButton and L1Button: 
                if DebugOn: print ("Test1")
                dalek_say("Test one")
            elif StartButton and L2Button: 
                if DebugOn: print ("Test2")
                dalek_say("Test two")
            elif StartButton and R1Button: 
                if DebugOn: print ("Test3")
                dalek_voice("1")
            elif StartButton and R2Button: 
                if DebugOn: print ("Test4")
                dalek_voice("2")

            #elif SelectButton:
            #    print ("Select")
            #elif StartButton:
            #    print ("Start")
            elif SquareButton:
                if DebugOn: print ("Square")
            elif XButton:
                if DebugOn: print ("X")
            elif CircleButton:
                if DebugOn: print ("Circle")
            elif TriangleButton:
                if DebugOn: print ("Triangle")
            elif YButton:
                if DebugOn: print ("Y")
            elif AButton:
                if DebugOn: print ("A")
            elif BButton:
                if DebugOn: print ("B")
            elif L1Button:
                print ("L1")
                if DutyCycleA < 100:
                   DutyCycleA = DutyCycleA + 10
                if DutyCycleB < 100:
                   DutyCycleB = DutyCycleB + 10
                DutyCycleA = min(DutyCycleA, 100)
                DutyCycleB = min(DutyCycleB, 100)
                if DebugOn: print "Speed: ", DutyCycleA, DutyCycleB
            elif R1Button:
                if DebugOn: print ("R1")
            elif L2Button:
                if DebugOn: print ("L2")
                if DutyCycleA > 0:
                   DutyCycleA = DutyCycleA - 10
                if DutyCycleB > 0:
                   DutyCycleB = DutyCycleB - 10
                DutyCycleA = max(DutyCycleA, 0)
                DutyCycleB = max(DutyCycleB, 0)
                if DebugOn: print "Speed: ", DutyCycleA, DutyCycleB
            elif R2Button:
                if DebugOn: print ("R2")
            elif L3Button:
                if DebugOn: print ("L3")
                if DebugOn: print "Switching to Left Stick"
                stick = "Left"
            elif R3Button:
                if DebugOn: print ("R3")
                if DebugOn: print "Switching to Right Stick"
                stick = "Right"
            elif LeftStickLeft and LeftStickUp and stick == "Left":
                FLeft()
            elif LeftStickLeft and LeftStickDown and stick == "Left":
                BLeft()
            elif LeftStickRight and LeftStickUp and stick == "Left":
                FRight()
            elif LeftStickRight and LeftStickDown and stick == "Left":
                BRight()
            elif LeftStickLeft and stick == "Left":
                Left()
            elif LeftStickRight and stick == "Left":
                Right()
            elif LeftStickUp and stick == "Left":
                Forwards()
            elif LeftStickDown and stick == "Left":
                Backwards()
            elif RightStickLeft and RightStickUp and stick == "Right":
                FLeft()
            elif RightStickLeft and RightStickDown and stick == "Right":
                BLeft()
            elif RightStickRight and RightStickUp and stick == "Right":
                FRight()
            elif RightStickRight and RightStickDown and stick == "Right":
                BRight()
            elif RightStickLeft and stick == "Right":
                Left()
            elif RightStickRight and stick == "Right":
                Right()
            elif RightStickUp and stick == "Right":
                Forwards()
            elif RightStickDown and stick == "Right":
                Backwards()
            
            if HatStickLeft:
                Left()
                if DebugOn: print ("Hat Left")
            elif HatStickRight:
                Right()
                if DebugOn: print ("Hat Right")
            elif HatStickUp:
                Forwards()
                if DebugOn: print ("Hat Up")
            elif HatStickDown:
                if DebugOn: print ("Hat Down")
                Backwards()
            
            if not LeftStickLeft and not LeftStickRight and not LeftStickUp and not RightStickDown and not RightStickLeft and not RightStickRight and not RightStickUp and not LeftStickDown and not HatStickLeft and not HatStickRight and not HatStickUp and not HatStickDown:
                StopMotors()
        time.sleep(interval)

# If CTRL+C is pressed, cleanup and stop
except KeyboardInterrupt:

    # Shut-down tweet
    dalek_stop()

    # Disable all drives
    StopMotors()

    # Re-center head servos
    wiringpi.pwmWrite(pinServo2,LookStraight)
    wiringpi.pwmWrite(pinServo1,LookForwards)
    
    # Reset GPIO settings
    GPIO.cleanup()
            
