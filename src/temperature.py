from flask import Blueprint, request, jsonify, g, current_app
import pymysql
import os
import MySQLdb
import logging
from datetime import datetime

temperatures = Blueprint('temperatures', __name__)

db_user = os.environ.get("DB_USER", "root")
db_password = os.environ.get("DB_PASSWORD", "password")
db_host = os.environ.get("DB_HOST", "localhost")
db_port = os.environ.get("DB_PORT", "3306")
db_name = os.environ.get("DB_NAME", "MeteoV6")

try:
    conn = MySQLdb.connect(
        user=db_user,
        passwd=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name
    )
    print("Conexiunea la baza de date a fost realizată cu succes.")
except Exception as e:
    print(f"Eroare la conectarea la baza de date: {e}")

try:
    cursor = conn.cursor()
    print("Cursorul a fost creat cu succes.")
except Exception as e:
    print(f"Eroare la crearea cursorului: {e}")

@temperatures.route('/api/temperatures', methods=['POST'])
def add_temperature():
    data = request.get_json()
    if 'valoare' in data and 'idOras' in data:
        id_oras = data['idOras']
        valoare = data['valoare']
    else:
        return jsonify({'error': 'Bad request'}), 400
    try:
        cursor.execute("INSERT INTO Temperaturi (id_oras, valoare, timestamp) VALUES (%s, %s, NOW(6));", (id_oras, valoare))
        conn.commit()
    except:
        return jsonify({'error': 'Conflict'}), 409
    cursor.execute("SELECT LAST_INSERT_ID();")
    temperature_id = cursor.fetchone()[0]
    return jsonify({'id': temperature_id}), 201

@temperatures.route('/api/temperatures', methods=['GET'])
def get_temperatures():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    from_date = datetime.strptime(
        request.args.get('from', default='1000-01-01', type=str),
        '%Y-%m-%d'
    ).strftime('%Y-%m-%d')
    until_date = datetime.strptime(
        request.args.get('until', default='9999-12-31', type=str),
        '%Y-%m-%d'
    ).strftime('%Y-%m-%d')

    asks = [f'ROUND({coord}, 3) = {value}' for coord, value in [('latitudine', lat), ('longitudine', lon)] if value]

    subclause = ''

    if asks:
        subclause = f' AND id_oras IN (SELECT id FROM Orase WHERE {" AND ".join(asks)})'

    cursor.execute(f"SELECT id, valoare, DATE_FORMAT(timestamp, '%Y-%m-%d') AS timestamp FROM Temperaturi WHERE timestamp BETWEEN '{from_date}' AND '{until_date}'{subclause}")

    temperature_list = [{'id': row[0], 'valoare': row[1], 'timestamp': row[2]} for row in cursor.fetchall()]
    return jsonify(temperature_list), 200
    
@temperatures.route('/api/temperatures/cities/<int:city_id>', methods=['GET'])
def get_temperatures_by_city(city_id):
    from_arg = request.args.get('from', default='1000-01-01')
    until_arg = request.args.get('until', default='9999-12-31')
    try:
        int_city_id = int(city_id)
    except ValueError:
        return jsonify({'error': 'Not found'}), 200
    cursor.execute(f"SELECT id,  valoare, DATE_FORMAT(timestamp, '%Y-%m-%d') AS timestamp FROM Temperaturi WHERE timestamp BETWEEN '{from_arg}' AND '{until_arg}' AND (id_oras = {int_city_id})")
    temperatures_list = [{'id': row[0], 'valoare': row[1], 'timestamp': row[2]} for row in cursor.fetchall()]
    return jsonify(temperatures_list), 200

@temperatures.route('/api/temperatures/countries/<int:country_id>', methods=['GET'])
def get_temperatures_by_country(country_id):
    from_arg = request.args.get('from', default='1000-01-01')
    until_arg = request.args.get('until', default='9999-12-31')
    try:
        int_country_id = int(country_id)
    except ValueError:
        return jsonify({'error': 'Not found'}), 200
    cursor.execute(f"SELECT id,  valoare, DATE_FORMAT(timestamp, '%Y-%m-%d') AS timestamp FROM Temperaturi WHERE timestamp BETWEEN '{from_arg}' AND '{until_arg}' AND id_oras IN (SELECT id FROM Orase WHERE id_tara = {int_country_id})")
    temperatures_list = [{'id': row[0], 'valoare': row[1], 'timestamp': row[2]} for row in cursor.fetchall()]
    return jsonify(temperatures_list), 200

@temperatures.route('/api/temperatures/<int:temperature_id>', methods=['PUT'])
def update_temperature(temperature_id):
    try:
        int_temperature_id = int(temperature_id)
    except ValueError:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json()
    if 'valoare' in data and 'idOras' in data:
        id_oras = data['idOras']
        valoare = data['valoare']
    else:
        return jsonify({'error': 'Bad request'}), 400
    try:
        cursor.execute("SELECT * FROM Temperaturi WHERE id=%s;", (temperature_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Temperature not found'}), 404
        cursor.execute("UPDATE Temperaturi SET id_oras=%s, valoare=%s, timestamp=NOW(6) WHERE id=%s;", (id_oras, valoare, temperature_id))
    except:
        return jsonify({'error': 'Conflict'}), 409
    conn.commit()
    return '', 200


@temperatures.route('/api/temperatures/<int:temperature_id>', methods=['DELETE'])
def delete_temperature(temperature_id):
    try:
        cursor.execute("SELECT * FROM Temperaturi WHERE id=%s;", (temperature_id,))
        existing_temperature = cursor.fetchone()
        if not existing_temperature:
            return jsonify({'error': 'Temperature not found'}), 404
        cursor.execute("DELETE FROM Temperaturi WHERE id=%s;", (temperature_id,))
    except:
        return jsonify({'error': 'Conflict'}), 409
    conn.commit()
    return '', 200

@temperatures.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db_conn') and g.db_conn is not None:
        g.db_conn.close()
