import config
import os
import utime
import urequests
import machine

mqtt_server = config.MQTT_SERVER

def download_file():
    server_url = f"http://{mqtt_server}:8000/ESP32/"
    file_list = []
    i = 0
    
    response = urequests.get(server_url)
    html = response.content.decode()
    
    # Find the start and end positions of href values
    start_pos = html.find('<a href="')
    end_pos = html.find('">', start_pos)

    while start_pos != -1 and end_pos != -1:
        # Extract the href value between the quotes
        href_content = html[start_pos + len('<a href="'):end_pos]
        file_list.append(href_content)

        # Find the start and end positions of the next href value
        start_pos = html.find('<a href="', end_pos)
        end_pos = html.find('">', start_pos)

    response.close()
    
    for file in file_list:
        i+=1
        response = urequests.get(server_url + file)
        if response.status_code == 200:
            print("downloading", response.content)
            f = open(file, "w")
            f.write(response.content)
            f.close()
            response.close()
        else:
            print(response.status_code)
        if i >= len(file_list):
            print("download file complete.")
            print("resetting machine...")
            utime.sleep(5)
            machine.reset()

def download_config(sensor_type):
    if sensor_type is not None:
        server_url = f"http://{mqtt_server}:8000/configs/{sensor_type}/config.py"
        response = urequests.get(server_url)
        if response.status_code == 200:
            print("downloading", response.content)
            f = open("config.py", "w")
            f.write(response.content)
            f.close()
            response.close()
            print("download config complete.")
            print("resetting machine...")
            utime.sleep(10)
            machine.reset()
        else:
            print(response.status_code)
