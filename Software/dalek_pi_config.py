# Initialisation
# --------------

from datetime import datetime

i = datetime.now()

# Enable / disable tweeting
TweetOn = False

# Enable / disable initial tweet at start-up
TweetStart = True

# Enable / disable final tweet at (controlled) shutdown
TweetStop = True

# Enable / disable debug functions
DebugOn = True

# Enable / disable camera functions
CameraOn = False

# Enable / disable motor control functions
DriveOn = True

# Enable / disable voicebox functions
VoiceOn = True

# Enable / disable remote control option
RemoteControl = True

# Start message
# -------------
#StartTweet = 'Happy 6th Birthday @Raspberry_Pi Dalek_Pi is now on-line, LIVE at the @CotswoldJam. Send tweet_help for instructions ' + i.strftime('%Y/%m/%d %H:%M:%S') 
#StartTweet = 'Dalek_Pi (v2.01.06) is now on-line. Send tweet_help for instructions ' + i.strftime('%Y/%m/%d %H:%M:%S') 
#StartTweet = 'Dalek_Pi (v2.01.07) is now on-line, LIVE in the Workshop at Wychwood 2018! Send tweet_help for instructions ' + i.strftime('%Y/%m/%d %H:%M:%S')
#StartTweet = 'Dalek_Pi (v2.01.08) is now on-line, LIVE at #RaspberryFields ! Send tweet_help for instructions ' + i.strftime('%Y/%m/%d %H:%M:%S')
#StartTweet = 'Dalek_Pi (v2.01.08) is now on-line, LIVE at the @CotswoldJam #rjam ! Send tweet_help for instructions ' + i.strftime('%Y/%m/%d %H:%M:%S')
StartTweet = 'Dalek_Pi (v2.01.08) is now on-line, LIVE at the #MarlboroughJam #rjam ! Send tweet_help for instructions ' + i.strftime('%Y/%m/%d %H:%M:%S')
#StartTweet = 'Dalek_Pi is now on-line Testing Testing Obey Obey Obey! ' + i.strftime('%Y/%m/%d %H:%M:%S')

# Stop Message
# ------------
StopTweet = 'Dalek_Pi is going off-line ' 

# YouTube Channel
# ---------------
# YouTubeCh = 'TBD'


# Photo path
photo_path = '/home/pi/Dalek_Pi/Photos/'

# Test Photo Image
test_photo_name = 'DalekPi-TestImage.jpg'
test_pic = '/home/pi/Dalek_Pi/Photos/' + test_photo_name

# Help sheet
help_image_name = 'help.jpg'
help_pic = '/home/pi/Dalek_Pi/Media/' + help_image_name

