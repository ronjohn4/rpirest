from flask import Flask, render_template, jsonify, request
import requests

server_url = 'http://10.0.0.132:5001/gpio/api/v1.0/'
app = Flask(__name__)


@app.route("/")
@app.route("/home")
def main():
    response = requests.get(server_url + 'pins/getstate')
    pins = response.json()
    pin_data = {
        'pins': pins
    }
    return render_template('RPiClient.html', **pin_data)


@app.route("/pinchange/<change_pin>/<action>")
def pinchange(change_pin, action):
    response = requests.put(server_url + 'pins/{0}/{1}'.format(change_pin, action))
    pins = response.json()
    pin_data = {
        'pins': pins
    }
    return render_template('RPiClient.html', **pin_data)


if __name__ == '__main__':
    app.run(debug=True)
