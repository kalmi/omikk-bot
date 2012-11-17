import os
from flask import Flask
import omikk

app = Flask(__name__)

@app.route('/kalmi_days_left')
def kalmi_days_left():
    days_left = omikk.get_days_left('12345678','DummyPassword')
    return str(days_left)

@app.route('/')
def hello():
    return 'Nope'

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)