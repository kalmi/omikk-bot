#encoding: utf-8
import os
from flask import Flask
from flask import stream_with_context, request, Response
from datetime import date
import omikk
import sendmail

app = Flask(__name__)

@app.route('/hidden/N4ndPLcaNTbpPpElP3Q116M44hrOV6HO84oaQIT4/receive_mail')
def receive_mail():
  return 'IGNORED'

@app.route('/hidden/N4ndPLcaNTbpPpElP3Q116M44hrOV6HO84oaQIT4/send_mails')
def send_mails():
    def generate():
      yield '<meta http-equiv="content-Type" content="text/html; charset=utf-8">'
      yield '<pre>'
      users = [
        {'uid':'12345678', 'password':'DummyPassword'},
      ]
      for user in users:
        yield "Fetching data for "
        yield user['uid']
        yield '\n'
        data = omikk.get_data(user['uid'],user['password'])
        days_left = (data['closest_expiration'] - date.today()).days
        if(days_left<=7):
          yield "Sending mail to "
          yield data['email']
          yield ' with content: '        
          content = 'Hátralévő napok a következő lejáratig: %d (%s)' % (days_left, data['closest_expiration'])
          yield content
          yield '\n'
          sendmail.send('',data['email'],'Könyvtári értesítő', content)
          yield 'Sent.\n'
        else:
          yield ' -> No action needed. \n'
        yield '\n'
          
      yield '</pre>'
    return Response(stream_with_context(generate()))    
    

@app.route('/kalmi_days_left')
def kalmi_days_left():
    user_data = omikk.get_data('12345678','DummyPassword')
    days_left = (user_data['closest_expiration'] - date.today()).days
    return str(days_left) + " days left (" + user_data['closest_expiration'] +")"

@app.route('/')
def hello():
    return 'Nope'

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)