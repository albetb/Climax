#!/usr/bin/python

import json
import sys
import time
import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT11

# Here the pin
DHT_PIN  = 4
HUM_PIN = 3

# Insert here the name of the file google give to you (DONT rename it)
GDOCS_OAUTH_JSON       = 'test-4510293f9e69.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'prova'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 30


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

	n=0
	n=n+1
	if n==100:
		n=0
    # Login if necessary.
	if worksheet is None:
		worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

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
#	try:
      eet.write(n, 0, datetime.datetime.now())
	res = worksheet.write(n, 1, temp)
	res = worksheet.write(n, 2, humidity)
	# print "\n"
	# import pudb; pu.db
#	except:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
#		print('Append error, logging in again')
#		worksheet = None
	time.sleep(FREQUENCY_SECONDS)
	continue

    # Wait 30 seconds before continuing
	print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
	time.sleep(FREQUENCY_SECONDS)
