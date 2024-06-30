#!/usr/bin/python3
"""
Flask web application:

Task Description
Set up a basic web server in your preferred stack.
Deploy it to any free hosting platform and expose an API endpoint that conforms to the criteria below:
Endpoint: [GET] <example.com>/api/hello?visitor_name="Mark" (where <example.com> is your server origin)

Response:
{
   "client_ip": "127.0.0.1", // The IP address of the requester
   "location": "New York" // The city of the requester
   "greeting": "Hello, Mark!, the temperature is 11 degrees Celcius in New York"
}
"""
from flask import Flask
from flask import request, jsonify
import requests as r


WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&current=temperature_2m"
GEO_LOCATION_URL = "https://get.geojs.io/v1/ip/geo/{}.json"

app = Flask(__name__)


def get_geo(ip):
    if ip is None:
        return None

    geo_obj = {"lat": None, "long": None, "location": None}

    req = r.get(GEO_LOCATION_URL.format(ip))
    json_res = req.json()
    if req.status_code != r.codes.ok:
        return None

    geo_obj['long'] = json_res.get('longitude')
    geo_obj['lat'] = json_res.get('latitude')
    geo_obj['location'] = json_res.get('city') if json_res.get('city') else \
        json_res.get('country')

    return geo_obj


def get_temp(geo_obj):
    if geo_obj is None:
        return None

    req = r.get(WEATHER_API_URL.format(geo_obj['lat'], geo_obj['long']))
    json_res = req.json()
    if req.status_code != r.codes.ok:
        return None

    return json_res.get('current', {}).get('temperature_2m')


@app.route('/api/hello', strict_slashes=False)
def hello():
    """
    This function defines what is to be returned by the given route
    """
    resp = {
        "client_ip": None,
        "location": None,
        "greeting": "Hello, {}!, the temperature is {} degrees Celcius in {}"
    }

    visitor_name = request.args.get('visitor_name', 'User')
    visitor_name = visitor_name.strip('\'"')

    resp['client_ip'] = request.headers.get('X-Real-IP', '127.0.0.1')
    geo_object = get_geo(resp['client_ip'])

    temp = get_temp(geo_object) if geo_object else None
    location = geo_object['location'] if geo_object else None

    resp['location'] = location
    resp['greeting'] = resp['greeting'].format(visitor_name, temp, location)

    return jsonify(resp), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')
