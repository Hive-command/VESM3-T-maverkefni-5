# ESP-Host


# boot.py -- run on boot-up
import network

# Replace the following with your WIFI Credentials
SSID = "TskoliVESM"
SSI_PASSWORD = "Fallegurhestur"


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSI_PASSWORD)
        while not sta_if.isconnected():
            pass
    print('Connected! Network config:', sta_if.ifconfig())


print("Connecting to your wifi...")
do_connect()

from network import WLAN, STA_IF
from espnow import ESPNow
from time import sleep_ms

import _thread

# Virkja þráðlausa netið
sta = WLAN(STA_IF)
sta.active(True)

sta.config(channel=5)

# Configure the ESP-NOW protocol and enable it
espnow = ESPNow()
espnow.active(True)

# Add a node (peer) that needs to communicate
hinn_esp_inn = b'4\x85\x18\x9c\xe7\xe4'  # MAC address-an á hinum ESP-inum
espnow.add_peer(hinn_esp_inn)

birtustig = -1
led = False


# def core0_thread():
def espnow_fall(mottaka):
    global birtustig
    global led
    # while True:
    # Receive message
    sendandi, skilabod = espnow.irecv(0)
    if skilabod:  # ef einhver skilaboð bárust (bytestring)
        # breytum bytestring í string (decode message)
        skilabod = skilabod.decode()
        # skilaboðin eru á forminu "birtustig led"
        birtustig = int(skilabod)
        print('___________')

        # Sendir state á LED til mælinga-ESP
        espnow.send(hinn_esp_inn, str(int(led)), False)
        print('Birtustig:', birtustig)
        print('LED:', int(led))
        print('___________')


# Tékkar hvort skilaboð hafi verið send frá hinum ESP-inum
espnow.irq(espnow_fall)

from machine import Pin, ADC
from microdot import Microdot, Response, send_file
from microdot_utemplate import render_template
from neopixel import NeoPixel

app = Microdot()
Response.default_content_type = 'text/html'


@app.route('/')
def index(request):
    return render_template('index.html', birtustig=birtustig, led_value=led)


@app.route('/toggle')
def toggle_led(request):
    global led
    print("Receive Toggle Request!")
    # led.value(not led.value())
    led = not led
    return "OK"


@app.route('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'


@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)


if __name__ == '__main__':
    app.run(debug=True)
