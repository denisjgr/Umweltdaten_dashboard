
from dash.dependencies import Input, Output, State

import requests
import psycopg2
from psycopg2 import sql
import dash
from dash import html, Dash, dcc
import plotly.express as px
import pandas as pd

DB_NAME = "Umweltdaten"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_HOST = "localhost"
DB_PORT = 5432

# SQL query to insert data
insert_temp_query = """
INSERT INTO temperature_data (box_ID, sensor_ID, timestamp, unit, messung)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""
insert_humidity_query = """
INSERT INTO humidity_data (box_ID, sensor_ID, timestamp, unit, messung)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""


def fetch_single_box_info(box_id):
    url = f"https://api.opensensemap.org/boxes/{box_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data from OpenSenseMap API for Box ID: {box_id}")
        return None


def fetch_multiple_box_info():
    date = "2024-06-14T00:00:00Z"
    bbox = "5.87,47.27,15.04,54.90"
    phenomenon = "temperature"
    url = f"https://api.opensensemap.org/boxes?bbox={bbox}&date={date}&phenomenon={phenomenon}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data
    else:
        print("Failed to fetch data from OpenSenseMap API")
        return None


def fetch_sensor_data(box_id, sensor_id, from_date, to_date):
    url = f"https://api.opensensemap.org/boxes/{box_id}/data/{sensor_id}?from-date={from_date}&to-date={to_date}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data from OpenSenseMap API for Box ID: {box_id}, Sensor ID: {sensor_id}")
        return None


def insert_data(box_id, sensor_id, data, data_type='temperature'):
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

        # Determine the correct insert query
        insert_query = insert_temp_query if data_type == 'temperature' else insert_humidity_query

        # Execute insert query for each data entry
        for entry in data:
            data_processed = (box_id, sensor_id, entry['createdAt'], '°C' if data_type == 'temperature' else '%', entry['value'])
            cursor.execute(insert_query, data_processed)

        # Commit the transaction
        connection.commit()
        print(f"Data inserted successfully into {data_type}_data table for Box ID: {box_id}, Sensor ID: {sensor_id}")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        connection.rollback()

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def query_data(sensor_id, table_name):
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()
        query = sql.SQL("SELECT timestamp, messung FROM {} WHERE sensor_ID = %s ORDER BY timestamp").format(sql.Identifier(table_name))
        cursor.execute(query, (sensor_id,))
        data = cursor.fetchall()
        return data

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Fetch and insert data from API into database initially
# Fetch and insert initial data from API into database for 10 boxes with both temp and humidity sensors
def fetch_and_insert_initial_data():
    boxes = fetch_multiple_box_info()
    inserted_boxes = 0
    for box in boxes:
        if inserted_boxes >= 10:
            print("10 Boxes inserted.")
            break

        box_id = box['_id']
        sensors = box['sensors']
        has_temperature = False
        has_humidity = False

        # Check if box has both temperature and humidity sensors
        for sensor in sensors:
            if sensor['unit'] == '°C':
                has_temperature = True
            elif sensor['unit'] == '%':
                has_humidity = True

        if has_temperature and has_humidity:
            # Fetch data for temperature sensor
            sensor_id_temp = next((sensor['_id'] for sensor in sensors if sensor['unit'] == '°C'), None)
            if sensor_id_temp:
                from_date = '2024-06-01T00:00:00Z'
                to_date = '2024-06-14T00:00:00Z'
                print(f"Fetching temperature data for Box ID: {box_id}, Sensor ID: {sensor_id_temp}")
                data_temp = fetch_sensor_data(box_id, sensor_id_temp, from_date, to_date)
                print(f"Inserting temperature data into database for Box ID: {box_id}, Sensor ID: {sensor_id_temp}")
                insert_data(box_id, sensor_id_temp, data_temp, 'temperature')

            # Fetch data for humidity sensor
            sensor_id_humidity = next((sensor['_id'] for sensor in sensors if sensor['unit'] == '%'), None)
            if sensor_id_humidity:
                from_date = '2024-06-01T00:00:00Z'
                to_date = '2024-06-14T00:00:00Z'
                print(f"Fetching humidity data for Box ID: {box_id}, Sensor ID: {sensor_id_humidity}")
                data_humidity = fetch_sensor_data(box_id, sensor_id_humidity, from_date, to_date)
                print(f"Inserting humidity data into database for Box ID: {box_id}, Sensor ID: {sensor_id_humidity}")
                insert_data(box_id, sensor_id_humidity, data_humidity, 'humidity')

            inserted_boxes += 1

    print("all boxes checked")


# Initialize Dash app
app = Dash(__name__)

# Layout of the Dash app
app.layout = html.Div(children=[
    html.H1(children='Weather Data Dashboard'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Dropdown(
        id='box-dropdown',
        options=[],
        value='',
        placeholder="Select a box"
    ),

    dcc.Graph(
        id='temperature-graph'
    ),

    dcc.Graph(
        id='humidity-graph'
    ),

    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # in milliseconds
        n_intervals=0
    )
])


# Callback to update dropdown options based on fetched boxes
@app.callback(
    Output('box-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_box_dropdown(n):
    boxes = fetch_multiple_box_info()
    if boxes:
        box_options = [{'label': box['name'], 'value': box['_id']} for box in boxes]
        return box_options
    else:
        return []


# Callback to update temperature graph based on selected box
@app.callback(
    Output('temperature-graph', 'figure'),
    Input('box-dropdown', 'value')
)
def update_temperature_graph(box_id):
    if not box_id:
        return {}

    # Fetch sensor ID for temperature dynamically
    box_info = fetch_single_box_info(box_id)
    if box_info:
        sensors = box_info['sensors']
        sensor_id_temp = next((sensor['_id'] for sensor in sensors if sensor['unit'] == '°C'), None)
        if sensor_id_temp:
            temperature_data = query_data(sensor_id_temp, 'temperature_data')
            if temperature_data:
                df = pd.DataFrame(temperature_data, columns=['timestamp', 'messung'])
                fig = px.line(df, x='timestamp', y='messung', title='Temperature Data')
                return fig

    return {}


# Callback to update humidity graph based on selected box
@app.callback(
    Output('humidity-graph', 'figure'),
    Input('box-dropdown', 'value')
)
def update_humidity_graph(box_id):
    if not box_id:
        return {}

    # Fetch sensor ID for humidity dynamically
    box_info = fetch_single_box_info(box_id)
    if box_info:
        sensors = box_info['sensors']
        sensor_id_humidity = next((sensor['_id'] for sensor in sensors if sensor['unit'] == '%'), None)
        if sensor_id_humidity:
            humidity_data = query_data(sensor_id_humidity, 'humidity_data')
            if humidity_data:
                df = pd.DataFrame(humidity_data, columns=['timestamp', 'messung'])
                fig = px.line(df, x='timestamp', y='messung', title='Humidity Data')
                return fig

    return {}

# Run the initial data fetch and insertion
fetch_and_insert_initial_data()

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
