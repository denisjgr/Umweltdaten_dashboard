# This is a sample Python script.
import requests
# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.


def fetch_single_box_info(box_id):
    url = f"https://api.opensensemap.org/boxes/{box_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data
    else:
        print("Failed to fetch data from OpenSenseMap API")
        return None


def fetch_multiple_box_info():
    limit = 1
    date = "2024-04-24T00:00:00Z"
    phenomenon = "temperature"
    minimal = "true"
    bbox = "5.87,47.27,15.04,54.90"
    url = f"https://api.opensensemap.org/boxes?bbox={bbox}&date={date}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data
    else:
        print("Failed to fetch data from OpenSenseMap API")
        return None


def fetch_sensor_data(box_id, sensor_id):
    url = f"https://api.opensensemap.org/boxes/{box_id}/data/{sensor_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data
    else:
        print("Failed to fetch data from OpenSenseMap API")
        return None


# Example usage
box_id = "5abeb022850005001b51d92f"
data = fetch_single_box_info(box_id)
data2 = fetch_multiple_box_info()

for station in data2:
    station_id = station['_id']
    print("Station ID:", station_id)
    station_name = station['name']
    print("Station Name:", station_name)
    station_sensors = station['sensors']
    for sensor in station_sensors:
        sensor_id = sensor['_id']
        print("Sensor ID:", sensor_id)
        sensor_title = sensor['title']
        print("Sensor Name:", sensor_title)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    print(data)
    box_id = "5abeb022850005001b51d92f"
    sensor_id = "5abeb022850005001b51d934"
    fetch_sensor_data(box_id, sensor_id)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
