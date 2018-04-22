# RPiServer
RPiServer exposes a simple set of APIs to read and change the Raspberry Pi pins.  The GPIO pin configuration depends on Raspberry Pi hardware so is implemented in the Server code.

## Installing GPIO on the Raspberry Pi

sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install python-rpi.gpio

sudo apt-get install python-pip

all comands can be run with python3 rather than python (which defaults to python 2)

# RPiClient
RPiClient displays a simple UI (using Flask) which displays the configured pins and their current state.  It interacts with the Raspberry Pi through the provided REST API endpoints.