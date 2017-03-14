#!/usr/bin/python

import json
import sys
import time
import datetime

import Adafruit_DHT
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import RPi.GPIO as GPIO

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT11

# Connected pin.
DHT_PIN  = 4
SOIL_PIN = 3

# Setup GPIO pin as input
GPIO.setmode(GPIO.BOARD)  
GPIO.setup(SOIL_PIN, GPIO.IN)

# Here insert the name of the json file google sent to you (DONT rename)
GDOCS_OAUTH_JSON       = 'test-4510293f9e69.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'Climax'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 300


def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
	#import pudb; pu.db
        scope =  ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)


print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
    # Login if necessary.
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

    if GPIO.input(SOIL_PIN):
	print('Soil wet')
	soil = 'wet'
    else:
	print('Soil dry')
	soil = 'dry'

    # Attempt to get sensor reading.
    humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor
    # can't be reliably read (timing is critical to read the sensor).
    if humidity is None or temp is None:
        time.sleep(2)
        continue

    print('Temperature: {0:0.1f} C'.format(temp))
    print('Humidity:    {0:0.1f} %'.format(humidity))

    # Append the data in the spreadsheet, including a timestamp
    try:
        res = worksheet.append_row((datetime.datetime.now(), temp, humidity, soil))
	# print "\n"
	# import pudb; pu.db
    except:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print('Append error, logging in again')
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue

    # Wait 30 seconds before continuing
    print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    time.sleep(FREQUENCY_SECONDS)
