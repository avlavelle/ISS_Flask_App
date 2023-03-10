#!/usr/bin/env python3

#Anna Victoria Lavelle
#AVL578
#March 5, 2023

from flask import Flask, request
from geopy.geocoders import Nominatim
import requests
import xmltodict
import math
import time
import yaml

app = Flask(__name__)

def get_data() -> dict:
    """
    Loads in the data from the ISS Trajectory Data website and puts it into a 
    dictionary.

    Args:
        None.

    Returns:
        data (dict): ISS Trajectory Data in a dictionary.
    """

    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.text)
    return data

gdata = get_data()

def get_config() -> dict:
    """
    Read a configuration file and return the associated value or default.

    Args:
        None.

    Returns:
        default_config (dict): Associated value or default from the configuration 
        file.
    """
    default_config = {"debug": True}
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_loaf(f)
    except Exception as e:
        print(f"Couldn't load the config file; details {e}")
    return default_config

@app.route('/', methods = ['GET'])
def all_data() -> list:
    """
    A route that allows users to return the entire data set from the ISS Trajectory
    Data.

    Args:
        None.

    Returns:
        epochs (list): List of the entire data set.
    """

    try:
        epochs = gdata['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return ("No data available")

    return epochs


@app.route('/epochs', methods = ['GET'])
def get_epochs() -> list:
    """
    A route that allows users to return a list of all of the Epochs in the data set.
    Offset and limit parameters can be used to return a specific list of Epochs.

    Args:
        offset (int): Results are offset by this integer.
        limit (int): Maximum number of results returned.

    Returns:
        sol (list): List of all of the Epochs in the data set.
    """

    
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', len(all_data()))
    if offset:
        try:
            offset = int(offset)
        except ValueError:
            return ("Enter a positive integer for offset.", 400)
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return ("Enter a positive integer for limit.", 400)
    try:
        epochs = gdata['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return ("No data available")

    sol = []
    counter = 0
    for epoch in epochs:
        if counter == limit:
            break
        if epochs.index(epoch) >= (offset):
            sol.append(epoch['EPOCH'])
            counter = counter + 1

    return sol

@app.route('/epochs/<string:epoch>', methods = ['GET'])
def get_vector(epoch: str) -> dict:
    """
    A route that allows the users to return the state vectors for a specific Epoch
    in the data set.

    Args:
        epoch (str): The specified Epoch.

    Returns:
        item (dict): Dictionary with the state vectors for the specified Epoch.
    """

    try:
        epochs = gdata['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return ("No data available")

    for item in epochs:
        if item['EPOCH'] == epoch:
            return item


@app.route('/epochs/<string:epoch>/location', methods = ['GET'])
def get_location(epoch: str) -> dict:
    """
    A route that allows the users to return the latitude, longitude, altitude, and 
    geoposition for a specific Epoch in the data set.

    Args:
        epoch (str): The specified Epoch.

    Returns:
        info (dict): Dictionary of the latitude longitude, altitude, and geoposition.
    """
    try:
        epochs = gdata['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return ("No data available")

    for item in epochs:
        if item['EPOCH'] == epoch:
            x = float(item['X']['#text'])
            y = float(item['Y']['#text'])
            z = float(item['Z']['#text'])
            hours = int(item['EPOCH'].split('T')[1].split(':')[0])
            mins = int(item['EPOCH'].split(':')[1])

    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    lon = math.degrees(math.atan2(y, x)) -((hours-12)+(mins/60))*(360/24)+32
    if (lon < -180):
        diff = 180 - abs(lon)
        lon = 180 + diff
    if (lon > 180):
        diff = lon - 180
        lon =-180+diff
    n = 15    
    alt = math.sqrt(x**2 + y**2 + z**2)-6371
    geocoder = Nominatim(user_agent='iss_tracker')
    try:
        loc = geocoder.reverse((32, -96), zoom = 5, language = 'en')
    except Error as e:
        return f'Geopy returned an error - {e}'

    geoloc = geocoder.reverse((lat,lon), zoom=n, language = 'en')
    while (geoloc == None) and (n > 1):
        n = n-1
        geoloc = geocoder.reverse((lat,lon), zoom=n, language = 'en')
    if (geoloc == None) and (n == 1):
        geoloc = "Over the Ocean"
    info = {"epoch": epoch, "latitude": str(lat)+ ' degrees', "longitude": str(lon)+ ' degrees', "altitude": str(alt)+ ' km', "geoposition": geoloc }
    return info

@app.route('/now', methods = ['GET'])
def get_now() -> dict:
    """
    A route that allows the users to return a dictionary of latitude, longitude, 
    altitude, speed, and geoposition of the Epoch that is nearest in time.

    Args:
        None.

    Returns:
        info (dict): Dictionary with latitude, longitude, altitude, speed, and 
        geoposition of the Epoch that is nearest in time.
    """

    try:
        epochs = gdata['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return ("No data available")

    time_now = time.time()
    diff = 100000000000000000000000000000
    for item in epochs:
        time_epoch = time.mktime(time.strptime(item['EPOCH'][:-5], '%Y-%jT%H:%M:%S'))
        difference = time_now-time_epoch
        if abs(difference) < diff:
            diff = abs(difference)
            finaldiff = difference
            epoch = item

    x = float(epoch['X']['#text'])
    y = float(epoch['Y']['#text'])
    z = float(epoch['Z']['#text'])
    hours = int(epoch['EPOCH'].split('T')[1].split(':')[0])
    mins = int(epoch['EPOCH'].split(':')[1])

    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
    lon = math.degrees(math.atan2(y, x)) -((hours-12)+(mins/60))*(360/24)+32
    if (lon < -180):
        difflo = 180 - abs(lon)
        lon = 180 + difflo
    if (lon > 180):
        diffla = lon - 180
        lon =-180+diffla
    n = 15    
    alt = math.sqrt(x**2 + y**2 + z**2)-6371
    geocoder = Nominatim(user_agent='iss_tracker')
    try:
        loc = geocoder.reverse((32, -96), zoom = 5, language = 'en')
    except Error as e:
        return f'Geopy returned an error - {e}'

    geoloc = geocoder.reverse((lat,lon), zoom=n, language = 'en')
    while (geoloc == None) and (n > 1):
        n = n-1
        geoloc = geocoder.reverse((lat,lon), zoom=n, language = 'en')
    if (geoloc == None) and (n == 1):
        geoloc = "Over the Ocean"
    info = {"closest epoch":epoch['EPOCH'] ,"latitude": str(lat)+ ' degrees', "longitude": str(lon)+ ' degrees', "altitude": str(alt)+ ' km', "geoposition": geoloc,"speed": get_speed(epoch['EPOCH'])['speed'], "seconds from now":str(finaldiff) + " s"  }
    return info
   



@app.route('/epochs/<string:epoch>/speed', methods = ['GET'])
def get_speed(epoch: str) -> dict:
    """
    A route that allows the users to return the instantaneous speed for a specific 
    Epoch.

    Args:
        epoch (str): The specificed Epoch.

    Returns:
        speed (dict): Dictionary with the instantaneous speed of the Epoch.
    """

    try:
        epochs = gdata['ndm']['oem']['body']['segment']['data']['stateVector']
    except KeyError:
        return ("No data available")
    for item in epochs:
        if item['EPOCH'] == epoch:
            xdot = float(item['X_DOT']['#text'])
            ydot = float(item['Y_DOT']['#text'])
            zdot = float(item['Z_DOT']['#text'])

    speed = math.sqrt(xdot**2+ydot**2+zdot**2)
    return {'speed': str(speed) + ' km/s'}

@app.route('/help', methods = ['GET'])
def get_help() -> str:
    """
    A route that provides help text for the user that describes each route.

    Args:
        None

    Returns:
        help (str): Help text for the user.
    """

    intro = "\nThese are the routes for iss_tracker.py.\n"
    
    head1 = "\nreturn elements from the data set\n"
    head2 = "\nedit or update the data set\n"
    head3 = "\nto receive help\n"
    one ="   / (GET)                                Return entire data set\n"
    two ="   /epochs (GET)                          Return list of all Epochs in the data set\n"
    thr ="   /epochs?limit=int&offset=int (GET)     Return modified list of Epochs given query parameters\n"
    fou ="   /epochs/<epoch> (GET)                  Return state vectors for a specific Epoch from the data set\n"
    fiv ="   /epochs/<epoch>/speed (GET)            Return instantaneous speed for a specific Epoch in the data set\n"
    six ="   /delete-data (DELETE)                  Delete all data from the dictionary object\n"
    sev ="   /post-data (POST)                      Reload the dictionary object with data from the web\n"
    eig ="   /help (GET)                            Return help text for the user\n"
    nin ="   /comment (GET)                         Return the comment object from the data set\n"
    ten ="   /header (GET)                          Return the header dictionary object from the data set\n"
    ele ="   /metadata (GET)                        Return the metadata dictionary object from the data\n" 
    twe ="   /epochs/<epoch>/location (GET)         Return latitude, longitude, altitude, and geoposition for a given Epoch\n"
    thi ="   /now (GET)                             Return latitude, longitude, altitude, speed, and geoposition for Epoch that is nearest in time\n\n"
    return intro + head1 + one + two + thr + fou + fiv + head2 + six + sev + head3 + eig + nin + ten + ele + twe + thi

@app.route('/delete-data', methods = ['DELETE'])
def delete_data() -> str:
    """
    A route that deletes all data from the dictionary object.

    Args:
        None

    Returns:
        (str): Statement about state of data.
    """
    global gdata
    gdata.clear()
    return ("Data has been deleted")

@app.route('/post-data', methods = ['POST'])
def post_data() -> str:
    """
    A route that reloads the dictionary object with data from the web.

    Args:
        None

    Returns:
        (str): Statement about state of data.
    """

    global gdata
    gdata = get_data()
    return ("Data has been restored")

@app.route('/comment', methods = ['GET'])
def get_comment() -> list:
    """
    A route that returns the 'comment' list object from the data set.

    Args:
        None.

    Returns:
        comment (list): Comment list object from the data set.
    """

    try:
        comment = gdata['ndm']['oem']['body']['segment']['data']['COMMENT']
    except KeyError:
        return ("No data available.")
    return comment

@app.route('/header', methods = ['GET'])
def get_header() -> dict:
    """
    A route that returns the 'header' dictionary object from the data set.

    Args:
        None.

    Returns:
        header (dict): Header dictionary object from the data set.
    """

    try:
        header = gdata['ndm']['oem']['header']
    except KeyError:
        return ("No data available.")
    return header

@app.route('/metadata', methods = ['GET'])
def get_meta() -> dict:
    """
    A route that returns the 'metadata' dictionary object from the data set.

    Args:
        None.

    Returns:
        meta (dict): Metadata dictionary object from the data set.
    """

    try:
        meta = gdata['ndm']['oem']['body']['segment']['metadata']
    except KeyError:
        return ("No data available.")
    return meta


if __name__ == '__main__':
    config = get_config()
    if config.get('debug', True):
        app.run(debug=True, host='0.0.0.0')
    else:
        app.run(host = '0.0.0.0')


