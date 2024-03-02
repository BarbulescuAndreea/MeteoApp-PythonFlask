from flask import Blueprint, request, jsonify, g
import pymysql
import os
import MySQLdb

cities = Blueprint('cities', __name__)
db_user = os.environ.get("DB_USER", "root")
db_password = os.environ.get("DB_PASSWORD", "password")
db_host = os.environ.get("DB_HOST", "localhost")
db_port = os.environ.get("DB_PORT", "3306")
db_name = os.environ.get("DB_NAME", "MeteoV6")
try:
    conn = MySQLdb.connect(
        user=db_user,
        password=db_password,
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

@cities.route('/api/cities', methods=['POST'])
def add_city():
    data = request.get_json()
    if 'nume' in data and 'lat' in data and 'lon' in data and 'idTara' in data:
        id_tara = data['idTara']
        nume = data['nume']
        lat = data['lat']
        lon = data['lon']
    else:
        return jsonify({'error': 'Bad request'}), 400
    try:
        cursor.execute("INSERT INTO Orase (id_tara, nume_oras, latitudine, longitudine) VALUES (%s, %s, %s, %s);", (id_tara, nume, lat, lon))
        conn.commit()
    except:
        return jsonify({'error': 'Conflict'}), 409
    # get the last inserted ID
    cursor.execute("SELECT LAST_INSERT_ID();")
    city_id = cursor.fetchone()[0]
    return jsonify({'id': city_id}), 201

@cities.route('/api/cities', methods=['GET'])
def get_cities():
    cursor.execute("SELECT id, id_tara, nume_oras, latitudine, longitudine FROM Orase;")
    cities_list = [{'id': row[0], 'idTara': row[1], 'nume': row[2], 'lat': row[3], 'lon': row[4]} for row in cursor.fetchall()]

    return jsonify(cities_list), 200

@cities.route('/api/cities/country/<int:country_id>', methods=['GET'])
def get_cities_by_country(country_id):
    try:
        int_country_id = int(country_id)
    except ValueError:
        return jsonify({'[]'}), 200
    cursor.execute("SELECT id, id_tara, nume_oras, latitudine, longitudine FROM Orase WHERE id_tara=%s;", (country_id,))
    cities_list = [{'id': row[0], 'idTara': row[1], 'nume': row[2], 'lat': row[3], 'lon': row[4]} for row in cursor.fetchall()]

    return jsonify(cities_list), 200

@cities.route('/api/cities/<int:city_id>', methods=['PUT'])
def update_city(city_id):
    try:
        int_city_id = int(city_id)
    except ValueError:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json()
    if 'nume' in data and 'lat' in data and 'lon' in data and 'idTara' in data:
        id_tara = data['idTara']
        nume = data['nume']
        lat = data['lat']
        lon = data['lon']
    else:
        return jsonify({'error': 'Bad request'}), 400
    try:
        # check if the city_id exists
        cursor.execute("SELECT id FROM Orase WHERE id=%s;", (city_id,))
        existing_city = cursor.fetchone()
        if not existing_city:
            return jsonify({'error': 'City with not found'}), 404

        cursor.execute("UPDATE Orase SET id_tara=%s, nume_oras=%s, latitudine=%s, longitudine=%s WHERE id=%s;", (id_tara, nume, lat, lon, city_id))
    except:
        return jsonify({'error': 'Conflict'}), 409
    conn.commit()
    return '', 200

@cities.route('/api/cities/<int:city_id>', methods=['DELETE'])
def delete_city(city_id):
    try:
        cursor.execute("SELECT id FROM Orase WHERE id=%s;", (city_id,))
        existing_city = cursor.fetchone()
        if not existing_city:
            return jsonify({'error': 'City with not found'}), 404
        cursor.execute("DELETE FROM Orase WHERE id=%s;", (city_id,))
    except:
        return jsonify({'error': 'Conflict'}), 409
    conn.commit()
    return '', 200

@cities.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db_conn') and g.db_conn is not None:
        g.db_conn.close()
