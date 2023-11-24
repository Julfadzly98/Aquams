# This file is executed on every boot (including wake-boot from deepsleep)
# import webrepl_setup
import esp

esp.osdebug(None)
#import webrepl
#webrepl.start(password='epdiot')
import network
import machine
import config

mqtt_server = config.MQTT_SERVER
wifi_ssid = config.WIFI_SSID
wifi_password = config.WIFI_PASSWORD
sensor_ip = config.SENSOR_IP

wlan = network.WLAN(network.STA_IF)
wlan.ifconfig((sensor_ip, '255.255.255.0', '192.168.0.1', '192.168.0.1'))
wlan.active(True)
if not wlan.isconnected():
    try:
        print('connecting to network...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            pass
    except Exception as e:
        print("machine restarting...")
        machine.reset()
print('network config:', wlan.ifconfig())
