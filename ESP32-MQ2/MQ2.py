import machine
import utime
import ubinascii
from umqttsimple import MQTTClient
import ujson
import uasyncio

class MQ2:
    def __init__(self, sensor_ip, mqtt_server, topic_pub, topic_sub, sensor_type):
        self.analog_pin = machine.ADC(machine.Pin(34))  # Replace with the analog pin connected to the MQ2 sensor
        # Other initialization code remains unchanged
        
    def read_sensor_value(self):
        # Read analog value from the sensor
        sensor_value = self.analog_pin.read()
        return sensor_value

    # The rest of the code (run method, MQTT handling, reboot_cronjob, etc.) stays mostly the same
    def sub_cb(self, topic, msg):
        if topic == b"server" and msg == b"download_scripts":
            print("updating code...")
            from ota import download_file
            download_file()
        if topic == b"server" and msg == b"download_configs":
            print("updating configs...")
            from ota import download_config
            download_config(self.sensor_type)

    def connect_and_subscribe(self):
        self.client = MQTTClient(self.client_id, self.mqtt_server)
        self.client.set_callback(self.sub_cb)
        self.client.connect()
        self.client.subscribe(self.topic_sub)
        print('Connected to %s MQTT broker, subscribed to %s topic' % (self.mqtt_server, self.topic_sub))
        return self.client

    def restart_and_reconnect(self):
        print('Failed to connect to MQTT broker. Reconnecting...')
        utime.sleep(10)
        machine.reset()

    async def reboot_cronjob(self):
        """ hard reset the ESP32 for every 24 hours at 00:00:00 """
        while True:
            await uasyncio.sleep(1)
            try:
                rtc = machine.RTC()
                """ the RTC will sync when there is has internet connection """
                current_datetime = rtc.datetime() # format is (year, month, day, weekday, hours, minutes, seconds, subseconds)
                if current_datetime[4] == 0 and current_datetime[5] == 0 and current_datetime[6] == 0:
                    print("reboot every 24 hours")
                    machine.reset()
            except BaseException as e:
                print("name resolution failed", e)

    async def run(self):
        while True:
            await uasyncio.sleep(1)
            try:
                self.client.check_msg()
                if (utime.time() - self.last_message) > self.message_interval:
                    try:
                        
                        self.DHT_sensor.measure()
                        temp = self.DHT_sensor.temperature()
                        hum = self.DHT_sensor.humidity()
                        temp_f = temp * (9/5) + 32.0
                        ujson_msg = {
                            "temp_c": float(round(temp, 2)),
                            "temp_f": float(round(temp_f, 2)),
                            "humidity": float(round(hum, 2))
                        }
                        msg_string = ujson.dumps(ujson_msg)
                        print(ujson_msg)
                        self.client.publish(self.topic_pub, msg_string)
                        self.last_message = utime.time()
                    except BaseException as e:
                        err_message = {
                            "temp_c": float(round(self.DHT_sensor.temperature(), 2)),
                            "temp_f": float(round(self.DHT_sensor.temperature(), 2)) * (9/5) + 32.0,
                            "humidity": float(round(self.DHT_sensor.humidity(), 2)),
                            "error": e
                        }
                        err_msg_string = ujson.dumps(err_message)
                        self.client.publish(self.topic_pub, err_msg_string)
            except OSError as e:
                self.restart_and_reconnect()
        
    async def run_async(self):
        await uasyncio.gather(self.reboot_cronjob(), self.run())
 
def start(sensor_ip, mqtt_server, topic_pub, topic_sub, sensor_type):
    dht = DHT(sensor_ip, mqtt_server, topic_pub, topic_sub, sensor_type)
    uasyncio.run(dht.run_async())
