
import requests

import psycopg2
from psycopg2 import sql

DB_NAME = "Umweltdaten"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

# SQL query to insert data
insert_query = """
INSERT INTO temperature_data (box_ID, sensor_ID, timestamp, unit, messung)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

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


def fetch_sensor_data(box_id, sensor_id, from_Date, to_Date):
    url = f"https://api.opensensemap.org/boxes/{box_id}/data/{sensor_id}?from-date={from_Date}&to-date={to_Date}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch data from OpenSenseMap API")
        return None

def insert_temp_data(box_id, sensor_id, temperature_data):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        # Create a cursor object
        cursor = connection.cursor()
        # Execute insert query for each data entry
        for entry in temperature_data:
            temperature_data_processed = (box_id, sensor_id, entry['createdAt'], '°C', entry['value'])   # box_ID, sensor_ID, timestamp, unit, messung
            cursor.execute(insert_query, temperature_data_processed)


        # Commit the transaction
        connection.commit()

        print("Data inserted successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()



# Example usage
#box_id = "5abeb022850005001b51d92f"
#data = fetch_single_box_info(box_id)
#data2 = fetch_multiple_box_info()

#for station in data2:
#    station_id = station['_id']
#    print("Station ID:", station_id)
#    station_name = station['name']
#    print("Station Name:", station_name)
#    station_sensors = station['sensors']
#    for sensor in station_sensors:
#        sensor_id = sensor['_id']
#        print("Sensor ID:", sensor_id)
#        sensor_title = sensor['title']
#        print("Sensor Name:", sensor_title)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    box_id = "661d89c21a903a0008f6e2e5"
    sensor_id = "661d89c21a903a0008f6e2e8"  # temperatur
    print("----------------------------------------------------\n\n\n\n")

    from_Date = '2024-05-01T00:00:00Z'
    to_Date = '2024-05-30T00:00:00Z'
    temperature_data = fetch_sensor_data(box_id, sensor_id, from_Date, to_Date)
    print(temperature_data)
    insert_temp_data(box_id, sensor_id, temperature_data)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

