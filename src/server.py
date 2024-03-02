from flask import Flask
import logging
from temperature import temperatures
from countries import countries
from cities import cities

server = Flask(__name__)
server.logger.setLevel(logging.DEBUG)
# blueprint - group the routes differently , connect parts of the app to the principal app
server.register_blueprint(temperatures)
server.register_blueprint(countries)
server.register_blueprint(cities)

if __name__ == "__main__":
	server.run('0.0.0.0',port=6000, debug=True)