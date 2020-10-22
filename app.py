# Import dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct


#################################################
# Database Setup
#################################################


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
conn = engine.connect()

# Reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def home():
    return(
        f"Welcome to the Hawaii Climate API!<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"Precipitation data by date:"
        f"<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"<br/>"
        f"<br/>"
        f"List of stations:"
        f"<br/>"
        f"/api/v1.0/stations <br/>"
        f"<br/>"
        f"<br/>"
        f"Temperature data by date for most active station for last twelve months of data:"
        f"<br/>"
        f"/api/v1.0/tobs <br/>"
        f"<br/>"
        f"<br/>"
        f"Min, max, and average temperature for all dates greater than start date:"
        f"<br/>"
        f"/api/v1.0/[start yyyy-mm-dd] <br/>"
        f"<br/>"
        f"<br/>"
        f"Min, max, and average temperature for dates between start and end date, inclusive:"
        f"<br/>"
        f"/api/v1.0/[start yyyy-mm-dd]/[end yyyy-mm-dd] <br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve precipitation measurements for each data
    sel = (Measurement.date, Measurement.prcp)
    results = session.query(*sel).all()
    
    session.close()

    # Convert the query results to a dictionary
    precipitation_dict = []
    index = 0
    for result in results:
        dict = {"date": results[index][0], "prcp": results[index][1]}
        index += 1
        precipitation_dict.append(dict)

    # Return JSON representation of dictionary
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve all of the station IDs
    results = session.query(Station.station).all()

    session.close()

    # Convert data to a regular list of station IDs
    stations = list(np.ravel(results))

    # Return JSON representation of station list
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    year_ago = "2016-08-23"

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to determine the most active station
    sel = (Measurement.station, func.count(Measurement.station))
    measurement_count_by_station = session.query(*sel).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active = measurement_count_by_station[0][0]

    # Query the last 12 months of temperature observation data for this station
    sel = (Measurement.station, Measurement.date, Measurement.tobs)
    results = session.query(*sel).filter_by(station=most_active).filter(Measurement.date>=year_ago).all()

    session.close()

    # Convert the query results to a dictionary
    temp_dict = []
    index = 0
    for result in results:
        dict = {"station": results[index][0], "date": results[index][1], "tobs": results[index][2]}
        index += 1
        temp_dict.append(dict)

    # Return JSON representation of temperature observation data for last 12 months
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def start(start):

    # Convert start date into a date-time object
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a querty to calculate the min, max, and average temperature for a specified date
    sel = (Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
    results = session.query(*sel).filter(Measurement.date >= start_date).all()

    session.close()

    # Create dictionary with station, min temperature, max temperature, and average temperature
    station = results[0][0]
    tmin = results[0][1]
    tmax = results[0][2]
    tavg = round(results[0][3], 1)
    temp_dict = {"station": station, "tmin": tmin, "tmax": tmax, "tavg": tavg}

    # Return JSON representation of temperature dictionary
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def date_range(start,end):
    
    # Convert start and end dates into date-time objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a querty to calculate the min, max, and average temperature for a specified date
    sel = (Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))
    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Create dictionary with station, min temperature, max temperature, and average temperature
    station = results[0][0]
    tmin = results[0][1]
    tmax = results[0][2]
    tavg = round(results[0][3], 1)
    temp_dict = {"station": station, "tmin": tmin, "tmax": tmax, "tavg": tavg}

    # Return JSON representation of temperature dictionary
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)