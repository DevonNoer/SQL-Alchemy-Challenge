# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import re

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#code for the main link showing the other links
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/><br>"
        f"-- Daily Precipitation Totals for Last Year: <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"-- Active Weather Stations: <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"-- Daily Tobs: <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"-- Min, Average & Max Temperatures for Date Range: /api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd<br>" 
    )
#flask code for precipitation for most recent year
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    first_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).order_by(Measurement.date.desc()).all()
    precDict = dict(results)
    session.close()
    return jsonify(precDict)

#code for the list of stations 
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stationData = session.query(Station.station).all()
    stationList = list(np.ravel(stationData))
    session.close()
    return jsonify(stationList)

#code for tobs of most active station
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    result = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date >= '2016-08-23').all()
    stationTobs = []
    for date, tobs in result:
        stationDict = {}
        stationDict["date"] = date
        stationDict["tobs"] = tobs
        stationTobs.append(stationDict)
    session.close()
    return jsonify(stationTobs)

#code for min, max, avg for given start date
@app.route("/api/v1.0/<start>")
def tempStart(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temp = []
    for min, avg, max in result:
        tempDict = {}
        tempDict["Min Temp"] = min
        tempDict["Avg Temp"] = avg
        tempDict["Max Temp"] = max
        temp.append(tempDict)
    session.close()
    return jsonify(temp)

#code for min, max, avg for given start date and end date
def tempStart(start, end):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp = []
    for min, avg, max in result:
        tempDict = {}
        tempDict["Min Temp"] = min
        tempDict["Avg Temp"] = avg
        tempDict["Max Temp"] = max
        temp.append(tempDict)
    session.close()
    return jsonify(temp)

if __name__ == '__main__':
    app.run(debug=True)