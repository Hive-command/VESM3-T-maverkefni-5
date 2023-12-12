# Mælinga-Sendir


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

from machine import Pin, ADC
from network import WLAN, STA_IF
from espnow import ESPNow
from time import sleep_ms

# Virkja þráðlausa netið
sta = WLAN(STA_IF)
sta.active(True)

sta.config(channel=5)

# Configure the ESP-NOW protocol and enable it
espnow = ESPNow()
espnow.active(True)

# Add a node (peer) that needs to communicate
hinn_esp_inn = b'4\x85\x18B\x80 '  # MAC address-an á hinum ESP-inum
espnow.add_peer(hinn_esp_inn)

ldr_pinni = ADC(Pin(8), atten=ADC.ATTN_11DB)
led = Pin(6, Pin.OUT)
led_sidast = 0

while True:
    # skilaboðin eru alltaf send sem strengur (eða bytestring)
    skilabod = str(ldr_pinni.read_u16())
    print('Birtustig:', skilabod)
    # Send a message
    espnow.send(hinn_esp_inn, skilabod, False)  # skilabod breytist í bytestring við sendingu
    # Receive message
    sendandi, skilabod = espnow.recv(0)
    if skilabod:  # ef einhver skilaboð bárust (bytestring)
        # breytum bytestring í string (decode message)
        skilabod = skilabod.decode()
        print('LED:', skilabod)
        print('_________')
        # skilaboðin eru á forminu "1" eða "0"
        led_value = int(skilabod)
        if led_value != led_sidast:
            led.value(not led.value())
            led_sidast = led_value

    sleep_ms(500)
