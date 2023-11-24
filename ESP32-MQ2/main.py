import config

mqtt_server = config.MQTT_SERVER
wifi_ssid = config.WIFI_SSID
wifi_password = config.WIFI_PASSWORD
sensor_type = config.SENSOR_TYPE
sensor_ip = config.SENSOR_IP
topic_pub = config.TOPIC_PUB
topic_sub = config.TOPIC_SUB

if sensor_type == "MQ2":
    print("MQ2")
    from MQ2 import start
    start(sensor_ip, mqtt_server, topic_pub, topic_sub, sensor_type)
elif sensor_type == "DHT":
    print("DHT")
    from DHT import start
    start(sensor_ip, mqtt_server, topic_pub, topic_sub, sensor_type)

