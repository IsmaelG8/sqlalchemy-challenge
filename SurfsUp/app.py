# Import the dependencies.
from flask import Flask, jsonify, send_from_directory
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

# Database Setup 
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"/plots/precipitation<br/>"
        f"/plots/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(recent_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).all()
    session.close()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()
    
    TMIN, TAVG, TMAX = results[0]
    
    return jsonify({
        "TMIN": TMIN,
        "TAVG": TAVG,
        "TMAX": TMAX
    })

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Placeholder implementation
    # You can expand this in a similar manner to start_date function
    return jsonify({"message": "Functionality for start_end_date to be implemented"})

@app.route("/plots/precipitation")
def plot_precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    precipitation_data = {date: prcp for date, prcp in results}

    dates = list(precipitation_data.keys())
    prcps = list(precipitation_data.values())

    plt.figure(figsize=(10,6))
    plt.plot(dates, prcps)
    plt.title("Precipitation over Time")
    plt.xlabel("Date")
    plt.ylabel("Precipitation")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/precipitation.png")
    
    return send_from_directory("static", "precipitation.png")

@app.route("/plots/tobs")
def plot_tobs():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(recent_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).all()
    session.close()

    temperatures = list(np.ravel(results))

    plt.figure(figsize=(10,6))
    plt.hist(temperatures, bins=12)
    plt.title("Frequency of Temperature Observations (TOBS)")
    plt.xlabel("Temperature")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("static/tobs.png")

    return send_from_directory("static", "tobs.png")

if __name__ == '__main__':
    app.run(debug=True)