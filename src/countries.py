from flask import Blueprint, request, jsonify, g
import pymysql
import os
import MySQLdb
countries = Blueprint('countries', __name__)

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

@countries.route('/api/countries', methods=['POST'])
def add_country():
    data = request.get_json()
    if 'nume' in data and 'lat' in data and 'lon' in data:
        nume = data['nume']
        lat = data['lat']
        lon = data['lon']
    else:
        return jsonify({'error': 'Bad request'}), 400
    try:
        cursor.execute("INSERT INTO Tari (nume_tara, latitudine, longitudine) VALUES (%s, %s, %s);", (nume, lat, lon))
        conn.commit()
    except:
        return jsonify({'error': 'Conflict'}), 409
    cursor.execute("SELECT LAST_INSERT_ID();")
    country_id = cursor.fetchone()[0]
    return jsonify({'id': country_id}), 201

# jsonify este o funcție în Flask care convertește obiecte Python în format JSON și construiește un răspuns HTTP JSON
@countries.route('/api/countries', methods=['GET'])
def get_countries():
    cursor.execute("SELECT id, nume_tara, latitudine, longitudine FROM Tari;")
    countries_list = [{'id': row[0], 'nume': row[1], 'lat': row[2], 'lon': row[3]} for row in cursor.fetchall()]

    return jsonify(countries_list), 200

@countries.route('/api/countries/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    try:
        int_country_id = int(country_id)
    except ValueError:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json()
    if 'nume' in data and 'lat' in data and 'lon' in data:
        nume = data['nume']
        lat = data['lat']
        lon = data['lon']
    else:
        return jsonify({'error': 'Bad request'}), 400
    try:
        cursor.execute("SELECT * FROM Tari WHERE id = %s;", (country_id,))
        existing_country = cursor.fetchone()
        if not existing_country:
            return jsonify({'error': 'Country not found'}), 404
        cursor.execute("UPDATE Tari SET nume_tara=%s, latitudine=%s, longitudine=%s WHERE id=%s;", (nume, lat, lon, country_id))
    except:
        return jsonify({'error': 'Conflict'}), 409
    conn.commit()
    return '', 200


@countries.route('/api/countries/<int:country_id>', methods=['DELETE'])
def delete_country(country_id):
    try:
        cursor.execute("SELECT * FROM Tari WHERE id = %s;", (country_id,))
        existing_country = cursor.fetchone()
        if not existing_country:
            return jsonify({'error': 'Country not found'}), 404
        cursor.execute("DELETE FROM Tari WHERE id=%s;", (country_id,))
    except:
        return jsonify({'error': 'Conflict'}), 409
    conn.commit()
    return '', 200

@countries.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db_conn') and g.db_conn is not None:
        g.db_conn.close()
