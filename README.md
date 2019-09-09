Installation
------------

Note: For the links to twitter, I used Alex Eames' very handy guide on using the Raspberry Pi to interface to twitter:

https://raspi.tv/2013/how-to-create-a-twitter-app-on-the-raspberry-pi-with-python-tweepy-part-1

(For Tweepy...)
1) sudo apt-get update
2) sudo apt-get install python-dev python-pip
3) sudo pip install -U pip
4) sudo pip install tweepy

(For WiringPi - used for h/w PWM)
5) sudo pip install wiringpi

(For speech)
6) sudo apt-get install festival

(Main program folder)
7) git clone https://github.com/astro-designs/Dalek_Pi.git