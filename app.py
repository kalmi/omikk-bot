#encoding: utf-8
import os

from flask import Flask
from flask_heroku import Heroku
from flask import stream_with_context, request, Response
from flask import render_template
import mailvalidator

from pytz import timezone
budapest = timezone('Europe/Budapest')

from datetime import datetime
def today(): 
  return datetime.now(budapest).date()
  
import omikk
import sendmail

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    omikk_uid = db.Column(db.String(20), unique=True)
    omikk_password = db.Column(db.String(20),nullable=False)
    last_checked = db.Column(db.Date,nullable=False)

    def __init__(self, email, omikk_uid, omikk_password):
        self.email = email
        
        self.omikk_uid = omikk_uid
        self.omikk_password = omikk_password
        
        self.last_checked = today()

    def __repr__(self):
        return '<E-mail %r>' % self.omikk_uid
  
@app.route('/hidden/EiRNnoEsuKwMcuOrhu6KZ7bnPgSTnkp2y6MLqobz/sendgrid_event')
def sendgrid_event(mail):
  event = request.form['event']
  email = request.form['email']
  
  if event == 'unsubscribe':  
    user = User.query.filter_by(email=email).first()
    db.session.delete(user)
    db.session.commit()
    return 'OK'
  else:
    return 'UNKOWN EVENT'
  
  
@app.route('/hidden/N4ndPLcaNTbpPpElP3Q116M44hrOV6HO84oaQIT4/send_mails')
def send_mails():
    def generate():
      #yield '<meta http-equiv="content-Type" content="text/html; charset=utf-8">'
      #yield '<pre>'
      
      for user in User.query.filter(User.last_checked != today()):
        
        yield 'Fetching data for '
        yield user.omikk_uid
        yield ' - '
        yield user.email
        yield '\n'
        data = omikk.get_data(user.omikk_uid, user.omikk_password)
        
        if(not mailvalidator.validate(data['email'])):
          yield "Mail not valid.\n\n"
          continue
        
        days_left = (data['closest_expiration'] - today()).days
        if(days_left<=7):
          yield "Sending mail to "
          yield data['email']
          yield ' with content: '        
          content = 'Hátralévő napok a következő lejáratig: %d (%s)' % (days_left, data['closest_expiration'])
          yield content
          yield '\n'
          sendmail.send('"OMIKK lejárat értesítő bot" <noreply@omikk.buuu.com>', data['email'], 'Könyvtári értesítő', content)
          yield 'Sent.\n'
        else:
          yield ' -> No action needed. \n'
          
        user.last_checked = today()
        db.session.commit()
        yield 'Last checked date commited.\n'
        yield '\n'
        
      #yield '</pre>'
    return Response(stream_with_context(generate()))    
    

@app.route('/kalmi_days_left')
def kalmi_days_left():
    user_data = omikk.get_data('12345678','DummyPassword')
    days_left = (user_data['closest_expiration'] - today()).days
    return "%s days left (%s)" % (days_left, user_data['closest_expiration'])

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    omikk_user = request.form['omikk_user']
    omikk_pass = request.form['omikk_pass']
    email = request.form['email']
    
    data = omikk.get_data(omikk_user, omikk_pass)
    if(data==False):
      return render_template('register.html', bad_attempt = True)
    else:
      User.query.filter(User.omikk_uid == omikk_user).delete()
      sendmail.remove_from_unsubscribe_list(email)
      user = User(email, omikk_user, omikk_pass)
      db.session.add(user)
      db.session.commit()
      days_left = (data['closest_expiration'] - today()).days
      return render_template('register_success.html', days_left = days_left)
  else:
    return render_template('register.html')
    
@app.route('/')
def hello():
    return 'Nope'

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)