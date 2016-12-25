#!/usr/bin/python -u
# Example of detecting and reading a block from a MiFare NFC card.
# Author: Tony DiCola
# Copyright (c) 2015 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import binascii
import sys

import Adafruit_PN532 as PN532

import os.path

from mpd import MPDClient
import time


dir="/home/pi/Musikkiste/"

# Setup how the PN532 is connected to the Raspbery Pi/BeagleBone Black.
# It is recommended to use a software SPI connection with 4 digital GPIO pins.

# Configuration for a Raspberry Pi:
CS   = 17
MOSI = 23
MISO = 24
SCLK = 25

# Configuration for a BeagleBone Black:
# CS   = 'P8_7'
# MOSI = 'P8_8'
# MISO = 'P8_9'
# SCLK = 'P8_10'

# Create an instance of the PN532 class.
pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)

# Call begin to initialize communication with the PN532.  Must be done before
# any other calls to the PN532!
pn532.begin()

# Get the firmware version from the chip and print(it out.)
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards.
pn532.SAM_configuration()

#datadict = { "cb5402c5" : "tunein:station:s45087",
#"309d9d90" : "file:///var/lib/mopidy/local/I%20Like%20To%20Move%20It%20Official%20Music%20Video-ecSCaZ_XPlo.m4a"
#}
def lookup ( id ):
	# check file present
	file = dir + id + ".m3u8"
	if os.path.isfile(file) and os.path.getsize(file) > 0:
		return file
		# return file contents
	else:
		# create empty file
		open(file, 'a').close()
		return None


# Main loop to detect cards and read a block.
print('Waiting for MiFare card...')
last = None
while True:
    # Check if a card is available to read.
    uid = pn532.read_passive_target()
    # Try again if no card is available.
    if uid == last:
        continue
    last = uid
    if uid is None:
        continue
    print('Found card with UID: 0x{0}'.format(binascii.hexlify(uid)))
    uid = binascii.hexlify(uid)
    file = lookup(uid)
    if file is None:
        continue
    print('Found file: ' + file)
    print('MPD communication start')
    client = MPDClient()
    client.timeout = 60
    client.connect("localhost", 6600)
    client.clear()
    client.load(uid)
    client.play()
    client.close()
    client.disconnect()
    print('MPD communication done')
    print('Waiting for MiFare card...')
        
