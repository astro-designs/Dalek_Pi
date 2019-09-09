#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# dalek_pi_twitter.py
# A program by Astro Designs Ltd @AstroDesignsLtd
# Control @Dalek_Pi using Twitter

import dalek_pi_config as dalek_pi
import dalek_pi_auth
import tweepy
from tweepy.api import API
import os
import sys
import subprocess
import Tkinter
from datetime import datetime

API_KEY = dalek_pi_auth.API_KEY
API_SECRET = dalek_pi_auth.API_SECRET
ACCESS_TOKEN = dalek_pi_auth.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = dalek_pi_auth.ACCESS_TOKEN_SECRET

key = tweepy.OAuthHandler(API_KEY, API_SECRET)
key.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(key)

DebugOn = dalek_pi.DebugOn
CameraOn = dalek_pi.DebugOn
DriveOn = dalek_pi.DriveOn

def dalek_start():
    global screen_name
    if dalek_pi.TweetStart == True:
        i = datetime.now()
        status = dalek_pi.StartTweet + i.strftime('%Y/%m/%d %H:%M:%S')
        print "Starting up... Tweeting:", status
        api.update_status(status=status)
    else:
        print "Starting up... (No Tweeting)"
    
def dalek_stop():
    global screen_name
    if dalek_pi.TweetStop == True:
        i = datetime.now()
        status = dalek_pi.StopTweet + i.strftime('%Y/%m/%d %H:%M:%S') 
        print "Shutting down... Tweeting:", status
        api.update_status(status=status)
    else:
        print "Shutting down... (No Tweeting)"

# Start-up tweet
dalek_start()

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
        tweet_split = tweet_rxd.split()
        tweet_rxd_data = status.user
        tweet_rxd_data = str(tweet_rxd_data)
        get_user()
        print "Sender: "+screen_name+" ("+user_name+")"
        print "Message:", tweet_rxd
        print tweet_split[0]
    
        if screen_name != "@Dalek_Pi":

			# Command Handler...
			if tweet_split[0] == 'move': # Deal with any movement requests from a separate function...
				if DriveOn == True:
					dalek_move()
				else:
					i = datetime.now()
					status = screen_name + ' ' + 'My drive is impared, I cannot move!: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
					api.update_status(status=status)
			elif tweet_split[0] == 'look': # Deal with any look requests from a separate function...
				dalek_look()
			elif tweet_split[0] == 'voice': # Deal with any look requests from a separate function...
				dalek_voice()
			elif tweet_split[0] == 'say': # Speak whatever comes next...
				dalek_say()
			elif tweet_split[0] == 'tweet_help': # Tweet the help-sheet back to whoever sent the tweet
				i = datetime.now()
				status = screen_name + ' ' + 'Help-sheet auto-tweet from Dalek_Pi: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
				print "testing tweet_help"
				api.update_with_media(dalek_pi.help_pic, status=status)
			elif tweet_split[0] == 'tweet_pic': # Take a picture & tweet it back to whoever sent the command
				i = datetime.now()
				if CameraOn == True:
					now = i.strftime('%Y%m%d-%H%M%S')
					photo_name = now + '.jpg'
					photo_path = dalek_pi.photo_path + photo_name
					print "Taking picture: " + photo_path
					bashCommand = ("raspistill -t 500 -hf -vf -w 1024 -h 768 -o " + photo_path)
					os.system(bashCommand)
					status = screen_name + ' ' + 'Photo auto-tweet from Dalek_Pi: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
				else:
					print "Camera is off-line. Sending test image"
					# Alternatively, send a test-image... Should probably define a global to enable / disable this...
					status = screen_name + ' ' + 'Sorry, my camera is off-line. I apologise for the inconvenience - Dalek_Pi: ' + i.strftime('%Y/%m/%d %H:%M:%S') 
				# Check if the file exists before tweeting...
				if os.path.exists(photo_path):
					 print "Tweeting image:" + photo_path
					 api.update_with_media(photo_path, status=status)
				elif os.path.exists(dalek_pi.test_pic):
					 print "Tweeting test image:" + dalek_pi.test_pic
					 api.update_with_media(dalek_pi.test_pic, status=status)
			elif tweet_split[0] == 'start_linefollow': # Start line-follower mode. May need to lock-out any other commands if this is running in the background
				bashCommand = ("pio spi-set 0x07 0")
				os.system(bashCommand)
				bashCommand = ("pio dalek-linefollower 1&")
				print "echo:"+bashCommand
				os.system(bashCommand)
			elif tweet_split[0] == 'stop_linefollow':
				bashCommand = ("pio spi-set 0x07 1")
				print "echo:"+bashCommand
				os.system(bashCommand)
			elif tweet_split[0] == 'say_exterminate':
				bashCommand = ("sudo ./text2speech.sh Exterminayte!")
				print "echo:"+bashCommand
				os.system(bashCommand)
			elif tweet_split[0] == 'Debug_On' and screen_name == "@AstroDesignsLtd":
				print "Turning on debug"
				DebugOn = True
			elif tweet_split[0] == 'Debug_Off' and screen_name == "@AstroDesignsLtd":
				print "Turning off debug"
				DebugOn = False
			elif tweet_split[0] == 'Drive_On' and screen_name == "@AstroDesignsLtd":
				print "Turning on drive"
				DriveOn = True
			elif tweet_split[0] == 'Drive_Off' and screen_name == "@AstroDesignsLtd":
				print "Turning off drive"
				DriveOn = False
			elif tweet_split[0] == 'Camera_On' and screen_name == "@AstroDesignsLtd":
				print "Turning camera on"
				CameraOn = True
			elif tweet_split[0] == 'Camera_Off' and screen_name == "@AstroDesignsLtd":
				print "Turning camera off"
				CameraOn = False
			elif tweet_split[0] == 'Exit' and screen_name == "@AstroDesignsLtd":
				dalek_stop()
				print "Exit command received & understood. Bye!"
				raise SystemExit
			elif tweet_split[0] == 'Reboot' and screen_name == "@AstroDesignsLtd":
				dalek_stop()
				bashCommand = ("sudo ./text2speech.sh Rebooting! Back in a jiffy")
				print "echo:"+bashCommand
				os.system(bashCommand)
				bashCommand = ("reboot")
				print "echo:"+bashCommand
				os.system(bashCommand)
			elif tweet_split[0] == 'Halt' and screen_name == "@AstroDesignsLtd":
				dalek_stop()
				bashCommand = ("sudo ./text2speech.sh Shutting down. Goodbye!")
				print "echo:"+bashCommand
				os.system(bashCommand)
				bashCommand = ("halt")
				print "echo:"+bashCommand
				os.system(bashCommand)
			elif tweet_split[0] == 'Shutdown' and screen_name == "@AstroDesignsLtd":
				dalek_stop()
				bashCommand = ("sudo ./text2speech.sh Shutting down. Goodbye!")
				print "echo:"+bashCommand
				os.system(bashCommand)
				bashCommand = ("shutdown")
				print "echo:"+bashCommand
				os.system(bashCommand)
			else:
				print "Command not recognised"
				print "Command: ", "\"", tweet_split[0], "\""
				print "Screen Name: ", screen_name
        else:
        	print "Ignoring own tweet:", "\"", tweet_rxd, "\""

        self.n = self.n+1
        if self.n < self.m: return True
        else:
        	print 'tweets = '+str(self.n)
        	return False
			
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
    print "New tweet from: "+screen_name+" ("+user_name+")"
    return

def dalek_say():
    global tweet_rxd, tweet_rxd_data, user_name
    tweet_rxd = tweet_rxd.lstrip(' say')
    tweet_rxd = tweet_rxd.lstrip(' ')
    print "Dalek_Speak: ",tweet_rxd
    command = 'sudo ./text2speech.sh '+tweet_rxd
    bashCommand = (str(command))
    print "echo:"+bashCommand
    os.system(bashCommand)

def dalek_move():
    global tweet_rxd
    tweet_rxd = tweet_rxd.lstrip(' move')
    print "move tweet_rxd:",tweet_rxd
    commands = tweet_rxd.split(',')
    print "No. Commands:",len(commands)
    for each in range(0, len(commands)):
        current_command = commands[each]
        print "current_command1:",current_command
        current_command = current_command.lstrip(' ')
        print "current_command2:",current_command
        split_current_command = current_command.split(' ')
        print "split_current_command:",split_current_command
        if len(split_current_command) == 2:
            if split_current_command[0] == "left":
                pio_command = "pio dalek-left"
            elif split_current_command[0] == "right":
                pio_command = "pio dalek-right"
            elif split_current_command[0] == "Back":
                pio_command = "pio dalek-backwards"
            elif split_current_command[0] == "back":
                pio_command = "pio dalek-backwards"
            elif split_current_command[0] == "backwards":
                pio_command = "pio dalek-backwards"
            elif split_current_command[0] == "Backwards":
                pio_command = "pio dalek-backwards"
            elif split_current_command[0] == "forward":
               pio_command = "pio dalek-forwards"             
            elif split_current_command[0] == "forwards":
               pio_command = "pio dalek-forwards"             
            else:
                print "Command not recognised"
                break # Exit for-loop if command isn't recognised

            value = split_current_command[1]
    
            bashCommand = (pio_command + " " +value)
            print "echo:"+bashCommand
            os.system(bashCommand)
    
def dalek_look():
    global tweet_rxd
    tweet_rxd = tweet_rxd.lstrip(' ')
    look_cmd = tweet_rxd.lstrip('look')
    look_cmd = look_cmd.lstrip(' ')
    look_cmd_split = look_cmd.split()
    print "look_cmd_split:",look_cmd_split
    if look_cmd_split[0] == "left":
        pio_command = "pio dalek-look-left"
    elif look_cmd_split[0] == "right":
        pio_command = "pio dalek-look-right"
    elif look_cmd_split[0] == "forwards":
        pio_command = "pio dalek-look-forwards"
    elif look_cmd_split[0] == "up":
        pio_command = "pio dalek-look-up"
    elif look_cmd_split[0] == "down":
        pio_command = "pio dalek-look-down"             
    else:
        print "Command not recognised"
        return
    
    bashCommand = (pio_command)
    print "echo:"+bashCommand
    os.system(bashCommand)

def dalek_voice():
    global tweet_rxd
    tweet_rxd = tweet_rxd.lstrip(' ')
    voice_cmd = tweet_rxd.lstrip('voice')
    voice_cmd = voice_cmd.lstrip(' ')
    voice_cmd_split = voice_cmd.split()
    print "voice_cmd_split:",voice_cmd_split
    if voice_cmd_split[0] == "1":
        pio_command = "pio dalek-speak 1"
    elif voice_cmd_split[0] == "2":
        pio_command = "pio dalek-speak 2"
    elif voice_cmd_split[0] == "3":
        pio_command = "pio dalek-speak 3"
    elif voice_cmd_split[0] == "4":
        pio_command = "pio dalek-speak 4"
    elif voice_cmd_split[0] == "5":
        pio_command = "pio dalek-speak 5"
    else:
        print "Command not recognised"
        return
    
    bashCommand = (pio_command)
    print "echo:"+bashCommand
    os.system(bashCommand)
    
stream = tweepy.streaming.Stream(key, Stream2Screen())
stream.filter(follow=['3997839202'], languages=['en'])
