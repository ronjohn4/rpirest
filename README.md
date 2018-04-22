# RPiREST
Keywords: Raspberry Pi, Flask, GPIO, REST API, jquery

There are 2 main components, RPiServer runs on the Raspberry Pi and exposes a set of APIs that allow RPiClient to
get/set the Raspberry Pi pin state.
Both Server and Client are written for Python 3.

# RPiServer
RPiServery runs on the Raspberry Pi and is tightly coupled with the Raspberry Pi hardware.  RPiServer is where you define
the pin settings.
Based on the pin settings, the pins are configured for Input or Output at start up.  The input pins have a REST endpoint
that can be called to set the pin.  Output pins have an interrupt set up which calls back to a RPiClient endpoint to
notify the client that a pin changed in real time.

## Installing GPIO on the Raspberry Pi
RPiServer depends on the GPIO library to interact with the pins.

sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install python-rpi.gpio

sudo apt-get install python-pip

# RPiClient
RPiClient displays a simple UI (using Flask) which displays the configured pins and their current state.  It
interacts with the Raspberry Pi through the provided REST API endpoints.