# Import the dependencies.
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################

# Reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    return jsonify({
        "Available Routes": [
            "/api/v1.0/precipitation",
            "/api/v1.0/stations",
            "/api/v1.0/tobs",
            "/api/v1.0/<start>",
            "/api/v1.0/<start>/<end>"
        ]
    })

#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = last_date - timedelta(days=365)

    # Query the precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Create a dictionary with date as the key and precipitation as the value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()
    stations_list = [station[0] for station in results]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year ago from the last data point
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    year_ago = last_date - timedelta(days=365)

    # Query temperature observations for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= year_ago).all()

    # Create a list of temperature observations
    temperature_data = [{date: tobs} for date, tobs in results]

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def start(start):
    # Query the minimum, average, and maximum temperatures for the specified start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temp_stats = results[0]

    return jsonify({
        "TMIN": temp_stats[0],
        "TAVG": temp_stats[1],
        "TMAX": temp_stats[2]
    })

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Query the minimum, average, and maximum temperatures for the specified start and end dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_stats = results[0]

    return jsonify({
        "TMIN": temp_stats[0],
        "TAVG": temp_stats[1],
        "TMAX": temp_stats[2]
    })

if __name__ == "__main__":
    app.run(debug=True)