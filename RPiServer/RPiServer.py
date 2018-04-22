# The pin key in the dict is string because json only supports strings.
# When it's an int it gets converted to string when jsonify().
# RPi.GPIO expects int.

# Ron Johnson
# 4/21/2018



import RPi.GPIO as GPIO
from flask import Flask, jsonify
import requests
import json


app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
url_client = 'http://10.0.0.224:5000'


# List of pins, name, direction and pull_up_down are assumed to be be static and based on the hardware
pins = {
    '17' : {'name' : 'GPIO 17', 'state' : GPIO.HIGH, 'direction' : GPIO.IN, 'pull_up_down' : GPIO.PUD_UP},
    '18' : {'name' : 'GPIO 18', 'state' : GPIO.HIGH, 'direction' : GPIO.IN, 'pull_up_down' : GPIO.PUD_UP},
    '19' : {'name' : 'GPIO 19 - yellow LED', 'state' : GPIO.LOW, 'direction' : GPIO.OUT, 'pull_up_down' : None},
    '16' : {'name' : 'GPIO 16 - blue LED', 'state' : GPIO.LOW, 'direction' : GPIO.OUT, 'pull_up_down' : None}
}


def pin_changed(channel):
    global pins

    pins[str(channel)]['state'] = GPIO.input(channel)
    payload = pins
    headers = {'content-type': 'application/json'}
    response = requests.put(url_client + '/serverpinchange/{0}/{1}'.format(channel, pins[str(channel)]['state']),
                            data = json.dumps(payload), headers=headers)
    if response.status_code != 200:
        print('pin_changed() error response:', response.status_code)


# Initialize pins at startup
def init_pins():
    for pin in pins:
        GPIO.setup(int(pin), pins[pin]['direction'])
        if pins[pin]['direction'] == GPIO.OUT:
            GPIO.setup(int(pin), pins[pin]['direction'])
            GPIO.output(int(pin), pins[pin]['state'])
        else:
            GPIO.setup(int(pin), GPIO.IN, pull_up_down=pins[pin]['pull_up_down'])
            GPIO.add_event_detect(int(pin), GPIO.BOTH, callback=pin_changed, bouncetime=10)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.route('/gpio/api/v1.0/pins/getstate', methods=['GET'])
def get_state():
    global pins

    for pin in pins:
        pins[pin]['state'] = GPIO.input(int(pin))

    return jsonify(pins)


@app.route('/gpio/api/v1.0/pins/<changePin>/<value>', methods=['PUT'])
def set_pin(changePin, value):
    global pins

    if changePin not in list(pins.keys()):
        raise InvalidUsage("pin={0} in not valid".format(changePin), status_code=410)

    if pins[changePin]['direction'] != GPIO.OUT:
        raise InvalidUsage("pin {} isn't set for output".format(changePin), status_code=410)

    if int(value) == GPIO.HIGH or int(value) == GPIO.LOW:
        GPIO.output(int(changePin), int(value))
    else:
        raise InvalidUsage("pin {0} can't be set to value={1}".format(changePin, value), status_code=410)

    for pin in pins:
        pins[pin]['state'] = GPIO.input(int(pin))

    return jsonify(pins)


if __name__ == '__main__':
    init_pins()
    app.run(host='10.0.0.132', debug=True)
