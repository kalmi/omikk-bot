#! /usr/bin/python

import smtplib
import requests, json
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send(fromEmail, toEmail, subject, content):
  # Create message container - the correct MIME type is multipart/alternative.
  msg = MIMEMultipart('alternative')
  msg['Subject'] = subject
  msg['From'] = fromEmail
  msg['To'] = toEmail

  # Create the body of the message (a plain-text and an HTML version).
  # text is your plain-text email
  # html is your html version of the email
  # if the reciever is able to view html emails then only the html
  # email will be displayed
  text = "%s\n" % content

  # Login credentials
  username = os.environ['SENDGRID_USERNAME']
  password = os.environ['SENDGRID_PASSWORD']

  # Record the MIME types of both parts - text/plain and text/html.
  part1 = MIMEText(text, 'plain', "utf-8")
  part2 = MIMEText(text, 'html', "utf-8")

  # Attach parts into message container.
  msg.attach(part1)
  msg.attach(part2)

  # Open a connection to the SendGrid mail server
  s = smtplib.SMTP('smtp.sendgrid.net', 587)

  # Authenticate
  s.login(username, password)

  # sendmail function takes 3 arguments: sender's address, recipient's address
  # and message to send - here it is sent as one string.
  s.sendmail(fromEmail, toEmail, msg.as_string())

  s.quit()
  
def remove_from_unsubscribe_list(email):
  payload = {
    'api_user': os.environ['SENDGRID_USERNAME'],
    'api_key': os.environ['SENDGRID_PASSWORD'],
    'email': email
  }
  resp = requests.get("https://sendgrid.com/api/unsubscribes.delete.json", params=payload)
  data = json.loads(resp.content)
  
  if(data[u'message'] != "success"):
    return False