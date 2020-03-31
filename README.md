# From satellite ID to groundtrack
> by [HULD](https://huld.io)

This is a tool to get the groundtrack from a certain satellite by having as input its satellite ID and the time at which the user wants to know its position. To find the ID of the satellite www.celestrak.com/NORAD/elements can be used. The website categorizes the satellites and give their respective TLE.

Example of TLE: 
```
ATLAS CENTAUR 2         
1 00694U 63047A   20090.82980658  .00000230  00000-0  13759-4 0  9990
2 00694  30.3601 323.7151 0585979 224.1186 131.1207 14.02586114825678
```
Its ID is then 00694.

Its groundtrack is calculated from the TLE using the orbit_predictor python libraries. 

# Setting the environment
## Requirements
* Docker installed
* Optionally PowerBI installed
* Create a USERNAME and PASSWORD for the https://www.space-track.org/ which you have to fill in the script.
## Update Secret.json
* See the examples in /secret_sample.json
* Update this file with outlook credentials and other parameters you wish tune
* Save it as a secret.json under /code/ directory (i.e /code/secret.json)

## Run following commands:
```
docker-compose build
docker-compose up
```
