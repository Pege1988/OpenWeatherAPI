# Program to retrieve data from openWeather API
# Version 1.0.0

import json
from urllib.request import urlopen
from datetime import datetime, date # to convert sunrise and sunset to time
import sqlite3
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#==============================================================
#   PARAMETERS
#==============================================================

# Test parameter (if test local, else synology)
test = True

# Filepaths
if test == True:
    data_path = r"C:\Users\neo_1\Dropbox\Projects\Programing\OpenWeatherAPI\Data"
    script_path = r"C:\Users\neo_1\Dropbox\Projects\Programing\OpenWeatherAPI"
else:
    data_path = "/volume1/homes/Pege_admin/Python_scripts"
    script_path = "/volume1/python_scripts/OpenWeatherAPI"

sql_file = "pege_db.sqlite"
conf_file = "confidential.txt"

sql_path = os.path.join(data_path, sql_file)
conf_path = os.path.join(script_path, conf_file)


# Get data from confidential file
confidential = []
with open(conf_path) as f:
    for line in f:
        confidential.append(line.replace("\n",""))
 
recipient = confidential[2]       
api_key = confidential[3]
city = confidential[4]
units = 'metric' # standard, metric, imperial
language = 'en' # en english, de german, fr french

#==============================================================
#   FUNCTIONS
#==============================================================

# Send Mail
def send_alarm(subject, recipient):
    host = "smtp-mail.outlook.com"
    port = 587
    password = confidential[1]
    sender = confidential[0]
    email_conn = smtplib.SMTP(host,port)
    email_conn.ehlo()
    email_conn.starttls()
    email_conn.login(sender, password)
    the_msg = MIMEMultipart("alternative")
    the_msg['Subject'] = subject 
    the_msg["From"] = sender
    the_msg["To"] = recipient
    # Create the body of the message
    message = """<html>
                    <head>
                        <title></title>
                    </head>
                    <body></body>
                </html>"""
    part = MIMEText(message, "html")
    # Attach parts into message container.
    the_msg.attach(part)
    email_conn.sendmail(sender, recipient, the_msg.as_string())
    email_conn.quit()

#==============================================================
#   SCRIPT
#==============================================================

# URL + file handle
try:
    url = 'http://api.openweathermap.org/data/2.5/weather?q='+city+'&appid='+api_key+'&units='+units+'&lang='+language
    html = urlopen(url).read()
    data = json.loads(html)
except:  
    send_alarm("ALERT: OpenWeather data could not be retrieved", recipient)

# Fetch Data
weather = data['weather'][0]
cloud=weather['main']
cloud_description=weather['description']
temperature = data['main']['temp']
feels_like = data['main']['feels_like']
temp_min = data['main']['temp_min']
temp_max = data['main']['temp_max']
pressure = data['main']['pressure']
humidity = data['main']['humidity']
visibility = data['visibility']
wind_speed = data['wind']['speed']
wind_deg = data['wind']['deg']
cloudiness = data['clouds']['all']
sunrise = datetime.utcfromtimestamp(int(data['sys']['sunrise'])).strftime('%Y-%m-%d %H:%M:%S')
sunset = datetime.utcfromtimestamp(int(data['sys']['sunset'])).strftime('%Y-%m-%d %H:%M:%S')

# Get date and time
today = date.today()
date = today.strftime("%d/%m/%Y")
now = datetime.now()
time = now.strftime("%H:%M:%S")

# Save data
try:
    conn = sqlite3.connect(sql_path)
    cur = conn.cursor()
    cur.execute('INSERT INTO openweather (cloud, cloud_description, temperature, feels_like, temp_min, temp_max, pressure, humidity, visibility, wind_speed, wind_deg, cloudiness, sunrise, sunset, date, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (cloud, cloud_description, temperature, feels_like, temp_min, temp_max, pressure, humidity, visibility, wind_speed, wind_deg, cloudiness, sunrise, sunset, date, time))
    conn.commit()
except:
    send_alarm("Data could not be stored", recipient)
    print("ALERT: OpenWeather data could not be stored")