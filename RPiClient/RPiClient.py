# pip install flask-socketio
# http://10.0.0.132:5001/gpio/api/v1.0/pins/getstate


from flask import Flask, render_template, flash, Response, jsonify, request
import requests
from flask_socketio import SocketIO, emit
import eventlet

eventlet.monkey_patch()

# todo - duplicated from RPi.GP
# Will be used when using and setting pin values
class GPIO():
    LOW = 0
    HIGH = 1
    OUT = 0
    IN = 1
    PUD_UP = 22

url_server = 'http://10.0.0.132:5001/gpio/api/v1.0/'
ip_client = '10.0.0.157'

pins = {}
app = Flask(__name__)
app.secret_key = 'some_secret'
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
namespace = ''  # set here and in the template to the same namespace

@app.route("/")
@app.route("/home")
def main():
    global pins

    response = requests.get(url_server + 'pins/getstate')
    pins = response.json()

    templateData = {
        'pins': pins
    }
    return render_template('RPiClient.html', **templateData, async_mode=socketio.async_mode)


@app.route("/pinchange/<changePin>/<action>")
def action(changePin, action):
    global pins
    global count

    response = requests.put(url_server + 'pins/{0}/{1}'.format(changePin, action))
    pins = response.json()
    # flash('pin change complete: pin={0} and state={1}'.format(changePin, action))

    templateData = {
        'pins' : pins
    }
    return render_template('RPiClient.html', **templateData, async_mode=socketio.async_mode)


@app.route("/serverpinchange/<changePin>/<action>", methods=['PUT'])
def serverchange(changePin, action):
    global pins

    pins = request.get_json()  #Flask request not requestS
    # flash('serverchange triggered with pin={0} and state={1}'.format(changePin, action))

    socketio.emit('my_response', {'pin': changePin, 'state': action}, namespace=namespace)
    return jsonify({'status': 'OK'})


if __name__ == '__main__':
    print(ip_client)
    socketio.run(app, host=ip_client, debug=True)
