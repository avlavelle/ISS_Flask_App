# Over the Ocean Somewhere: Tracking the ISS

This project is compiled of one script that builds a Flask application and provides thirteen different routes for the user to query that each return different pieces of information about the ISS, using the ISS Trajectory Data from NASA. The project also includes a Dockerfile that allows any user to pull the image from Docker Hub and run an instance of the image into a container on their personal machine, as well as a Docker compose file that allows a user to start the container easily and succinctly.

The Flask application routes are important because the ISS Trajectory Data contains loads of information that may not be interesting to the user. The Flask application and the routes allow users to quickly query the information that they may be looking for without having to comb through the data manually. The Dockerfile allows any user to have access to these capabilities through running an instance of the image on their own machine, plus the Docker compose file automates the deployment of the application, so the container is easy to start. 

## Accessing and Describing the Data
 
The ISS Trajectory Data is loaded in from this link, https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS\_OEM/ISS.OEM\_J2K\_EPH.xml , where the data is in XML format. The application loads it into a dictionary, and each route combs through the many dictionaries embedded in the data set to return what the user is looking for. The data mainly contains state vectors, {X, Y, Z} and {X\_DOT, Y\_Dot, Z\_DOT} in km/s for different time stamped locations of the ISS in reference to Earth and the J2000 reference frame.

## Flask App and Its Routes

The Flask application contains a function that loads in the data and different routes that return calculations or different information from the data set. The routes return information from the entire data set to the instantaneous velocity of a specified Epoch to the location of the Epoch that is closest to real time. The ```/help``` route offers descriptions of every route within the application.

## Pulling the Image and Running the App

Install the project by cloning the repository. 

Use ```docker pull avlavelle/midterm_iss``` to pull a copy of the container.
Then, ```docker-compose up``` will get the container running using the compose file, build the image, and bind the appropriate port inside the container to the appropriate port on the host.

In a separate window, you can use ``` curl localhost:5000 ``` to call the routes.

## Building a New Image from the Dockerfile

In order to build a new image from the Dockerfile, use the same ```docker pull``` command from above. 
Then, use ```docker-compose build``` to build the image and use ```docker images``` to check that a copy of the image has been built.

## Example Queries and Interpretation of Results

For ```/``` which returns the entire data set:
```
{"EPOCH": ..., "X": {"#text": ..., "@units": ...}, "X_DOT": {"#text": .../ "@units": ...},...}
```
This continues for the entire data set and also includes {Y, Z} and {Y_DOT, Z_DOT} in the state vectors. Those were excluded in this example for simplicity purposes.

For ```/epochs``` which returns a list of all Epochs in the data set or ```/epochs?limit=int&offset=int``` which returns a modified list of Epochs given query parameters:
```
["2023-048T12:00:00.000Z", ... ,"2023-063T12:00:00.000Z"]
```
For ```/epochs/<epoch>``` which returns the state vectors for a specific Epoch:
```
{"EPOCH": ..., "X": {"#text": ..., "@units": ...}, "X_DOT": {"#text": .../ "@units": ...}}
```
This returns only one Epoch and its state vectors, including {Y,Z} and {Y_DOT, Z_DOT}, which are excluded here.

For ```/epochs/<epoch>/speed``` which returns the instantaneous speed for a specific Epoch:

```
{"speed": "... km/s"}
```
For ```/help``` which returns help text describing the routes:
```
These are the routes for iss_tracker.py.

return elements from the data set
   / (GET)                          Return entire data set
```
The rest of the ```/help``` route descriptions are excluded here.

For ```/delete-data``` which deletes all data from the dictionary object:
```
Data has been deleted
```

For ```/post-data``` which reloads the dictionary object with data from the ISS Trajectory link:
```
Data has been restored
```

For ```/comment``` which returns the comment list object from the data:
```
["Units are in kg and m^2","Mass=473291.00", "..."]
```

For ```/header``` which returns the header dictionary object from the data:
```
{"CREATION_DATE": "...", "ORIGINATOR": "..."}
```

For ```/metadata``` which returns the metadata dictionary object from the data:
```
{"CENTER_NAME": "..." , ... ,"TIME_SYSTEM": "..."}
```

For ```/epochs/<epoch>/location``` which returns the lat, lon, alt, and geoposition for an Epoch:
```
{"altitude": "..." , ... ,"longitude": "..."}
```

For ```/now``` which returns the lat, lon, alt, geoposition, speed, and time difference for the Epoch that is nearest in time:
```
{"altitude": "..." , ... , "speed": "..."}
```
