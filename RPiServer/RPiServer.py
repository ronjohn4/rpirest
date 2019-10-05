# The pin key in the dict is string because json only supports strings.
# When it's an int it gets converted to string on jsonify().
# RPi.GPIO expects int.
#
# Install GPIO (pip install not available):
# sudo apt-get -y install python3-rpi.gpio

# todo - add logging
#
# Ron Johnson
# 4/21/2018


from flask import Flask, jsonify
import requests
import json
import socket
import logging
from logging.handlers import RotatingFileHandler
import os
import RPi.GPIO as GPIO

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
url_client = None
server_port = 5001

# List of pins, name, direction and pull_up_down.
# Defined static on the server because it's based on the hardware attached to the server.
pins = {
    '16': {'name': 'GPIO 16 - blue LED',
           'state': GPIO.LOW,
           'direction': GPIO.OUT,
           'pull_up_down': None},
    '17': {'name': 'GPIO 17',
           'state': GPIO.HIGH,
           'direction': GPIO.IN,
           'pull_up_down': GPIO.PUD_UP},
    '18': {'name': 'GPIO 18',
           'state': GPIO.HIGH,
           'direction': GPIO.IN,
           'pull_up_down': GPIO.PUD_UP},
    '19': {'name': 'GPIO 19 - yellow LED',
           'state': GPIO.LOW,
           'direction': GPIO.OUT,
           'pull_up_down': None}
}


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def pin_changed(channel):
    global pins
    global url_client

    pins[str(channel)]['state'] = GPIO.input(channel)
    app.logger.debug('pins changed:{0}'.format(pins))

    if url_client is None:
        app.logger.info("Client url not set, can't inform client of the change.  Client needs to call the "
                        "'http://{0}:{1}/gpio/api/v1.0/clientip/<clientIP>' Server endpoint to set the Client url."
                        .format(get_ip(), server_port))
    else:
        payload = pins
        headers = {'content-type': 'application/json'}
        app.logger.debug('{0}/serverpinchange/{1}/{2}'.format(url_client, channel, pins[str(channel)]['state']))
        response = requests.put('{0}/serverpinchange/{1}/{2}'.format(url_client, channel, pins[str(channel)]['state']),
                                data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            app.logger.info('pin_changed() error response:{0}'.format(response.status_code))


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
def set_pin(change_pin, value):
    global pins

    if change_pin not in list(pins.keys()):
        app.logger.info("pin={0} in not valid".format(change_pin))
        raise InvalidUsage("pin={0} in not valid".format(change_pin), status_code=410)
    if pins[change_pin]['direction'] != GPIO.OUT:
        app.logger.info("pin {} isn't set for output".format(change_pin))
        raise InvalidUsage("pin {} isn't set for output".format(change_pin), status_code=410)
    if int(value) == GPIO.HIGH or int(value) == GPIO.LOW:
        GPIO.output(int(change_pin), int(value))
    else:
        app.logger.info("pin {0} can't be set to value={1}".format(change_pin, value))
        raise InvalidUsage("pin {0} can't be set to value={1}".format(change_pin, value), status_code=410)
    for pin in pins:
        pins[pin]['state'] = GPIO.input(int(pin))
    return jsonify(pins)


@app.route('/gpio/api/v1.0/clientip/<clientIP>', methods=['POST'])
def set_client(client_ip):
    global url_client

    url_client = 'http://' + client_ip
    app.logger.info('Client url set to: {0}'.format(url_client))
    app.logger.info('Test using curl from the Rpi Server: curl -X PUT {0}:{1}/<pin>/1'.format(url_client, server_port))
    return jsonify(pins)

print('starting')
if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/rpiserver.log', maxBytes=20480, backupCount=20)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(file_handler.level)

    app.logger.info('RPiServer startup =========================================')
    print('starting main')

    init_pins()
    app.run(host='10.0.0.132', port=server_port, debug=True)
