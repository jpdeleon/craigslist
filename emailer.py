#!/usr/bin/env python
"""
UNDER DEVELOPMENT
https://julien.danjou.info/sending-emails-in-python-tutorial-code-examples/

Created on Tue May 12, 2020
@author: jpdeleon
"""
import smtplib
from socket import gaierror

port = 2525
smtp_server = "smtp.mailtrap.io"
login = "9c8c1a9088047a" # from Mailtrap
password = "f32c6691b28897" # from by Mailtrap


# Specify the sender’s and receiver’s email addresses:
sender = f"9c8c1a9088047a@{smtp_server}"
receiver = "jpdeleon.bsap@gmail.com"

# Type your message: use two newlines (\n) to separate the subject from the message body
message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}
This is my first message with Python."""

try:
  # Send your message with credentials specified above
  with smtplib.SMTP(smtp_server, port) as server:
    server.login(login, password)
    server.sendmail(sender, receiver, message)
except (gaierror, ConnectionRefusedError):
  # tell the script to report if your message was sent or which errors need to be fixed
  print('Failed to connect to the server. Bad connection settings?')
except smtplib.SMTPServerDisconnected:
  print('Failed to connect to the server. Wrong user/password?')
except smtplib.SMTPException as e:
  print('SMTP error occurred: ' + str(e))
else:
  print('Sent')
