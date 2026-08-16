import joblib      # used for loading/saving machine‑learning models.
import numpy as np
import pandas as pd 
import csv
import random
import wandb
import os
from fastapi import FastAPI, HTTPException, status
# FastAPI: framework for building APIs.
# HTTPException: used to raise API errors.
# status: provides HTTP status codes.
from pydantic import BaseModel, Field   # defines request/response schemas with validation.
from typing import List
from datetime import datetime 
import psycopg


def import_model():
    model = None 
    
    try:
        # Attempts to load the saved model file
        api = wandb.Api()
        artifact = api.artifact("claire-coughran-university-of-denver/U.S. Flight Delay Prediction/log_reg_v5:v0", type="model")
        artifact_dir = artifact.download()
        files = os.listdir(artifact_dir)
    
        # Load the first .pkl file found
        pkl_files = [f for f in files if f.endswith(".pkl")]
        if not pkl_files:
            raise FileNotFoundError("No .pkl file found in artifact")
    
        model_path = os.path.join(artifact_dir, pkl_files[0])
        model = joblib.load(model_path)
        print("Model loaded successfully!")
        
    except Exception as e:
        print("Error loading model from W&B:", e)
        
    return model


model = import_model()

    # Define the input schema for prediction requests
class FlightInput(BaseModel):
    # Expects a JSON body containing a list of numerical features
    MONTH: int
    OP_UNIQUE_CARRIER: str
    ORIGIN: str
    DEST: str
    DEP_DELAY_NEW: int
    DEP_TIME_BLK: float
    TAXI_OUT: float
    CANCELLED: float
    DIVERTED: float
    CRS_ELAPSED_TIME: float
    DISTANCE: float
    CARRIER_DELAY: float
    WEATHER_DELAY: float
    NAS_DELAY: float
    SECURITY_DELAY: float
    LATE_AIRCRAFT_DELAY: float
    LONGEST_ADD_GTIME: float
    DIV_AIRPORT_LANDINGS: float
    WEEKEND: float

class FlightRequest(BaseModel):
    features: FlightInput
    true_delay: int 


# Create the FastAPI application instance
app = FastAPI(title="U.S. Flight Delay-Prediction",)

# Startup event: runs once when the API boots
@app.on_event("startup")
def startup_event():
    # Checks if the model was loaded correctly. If not, it prints a persistent warning.
    if model is None:
        print("WARNING: Model is not loaded. Prediction endpoints will not work.")


@app.get("/")
def read_root():
    return {"Hello": "World"}

    
# Health check endpoint
@app.get("/health")
def health_check():
    # Confirm that the API is running.
    return {"status": "ok"}


# Prediction endpoint (binary output)
@app.post("/predict")
def predict(input_data: FlightRequest):
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not loaded. Cannot make predictions.")

    input_df = pd.DataFrame([input_data.features.dict()])
    
    start = datetime.utcnow()
    
    prediction = model.predict(input_df)[0]

    end = datetime.utcnow()

    timestamp = start.isoformat() 

    prediction_latency = (end - start).total_seconds()
        
    # upload log_entry to rds postgre 
    conn = psycopg.connect(
    host="us-flight-delay-prediction-log.cdaaom8syj04.us-east-2.rds.amazonaws.com",
    port=5432,
    dbname="FlightDelayPredictionLog",
    user="postgres",
    password=os.getenv("DB_PASSWORD"))

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO prediction_logs (
                timestamp,
                month,
                op_unique_carrier,
                origin,
                dest,
                dep_delay_new,
                dep_time_blk,
                taxi_out,
                cancelled,
                diverted,
                crs_elapsed_time,
                distance,
                carrier_delay,
                weather_delay,
                nas_delay,
                security_delay,
                late_aircraft_delay,
                longest_add_gtime,
                div_airport_landings,
                weekend,
                predicted_delay,
                true_delay, 
                prediction_latency)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (timestamp,
                input_data.features.MONTH,
                input_data.features.OP_UNIQUE_CARRIER,
                input_data.features.ORIGIN,
                input_data.features.DEST,
                input_data.features.DEP_DELAY_NEW,
                input_data.features.DEP_TIME_BLK,
                input_data.features.TAXI_OUT,
                input_data.features.CANCELLED,
                input_data.features.DIVERTED,
                input_data.features.CRS_ELAPSED_TIME,
                input_data.features.DISTANCE,
                input_data.features.CARRIER_DELAY,
                input_data.features.WEATHER_DELAY,
                input_data.features.NAS_DELAY,
                input_data.features.SECURITY_DELAY,
                input_data.features.LATE_AIRCRAFT_DELAY,
                input_data.features.LONGEST_ADD_GTIME,
                input_data.features.DIV_AIRPORT_LANDINGS,
                input_data.features.WEEKEND,
                prediction,
                input_data.true_delay, 
                prediction_latency))

    conn.commit()
    conn.close()
        
    return {"delay": prediction}
    

@app.get("/example")
def train_example():
    target = random.randint(1, 50000)

    with open("clean_delays.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

        arr_idx = header.index("ARR_DEL15")
        
        for i, row in enumerate(reader, start=1):
            if not row: continue  # skip empty rows
                
            if i == target: 
                true_delay = row[arr_idx]
                feature_vals = row[:arr_idx] + row[arr_idx+1:]

                flight_input = FlightInput(
                    MONTH=feature_vals[0],
                    OP_UNIQUE_CARRIER=feature_vals[1],
                    ORIGIN=feature_vals[2],
                    DEST=feature_vals[3],
                    DEP_DELAY_NEW=feature_vals[4],
                    DEP_TIME_BLK=feature_vals[5],
                    TAXI_OUT=feature_vals[6],
                    CANCELLED=feature_vals[7],
                    DIVERTED=feature_vals[8],
                    CRS_ELAPSED_TIME=feature_vals[9],
                    DISTANCE=feature_vals[10],
                    CARRIER_DELAY=feature_vals[11],
                    WEATHER_DELAY=feature_vals[12],
                    NAS_DELAY=feature_vals[13],
                    SECURITY_DELAY=feature_vals[14],
                    LATE_AIRCRAFT_DELAY=feature_vals[15],
                    LONGEST_ADD_GTIME=feature_vals[16],
                    DIV_AIRPORT_LANDINGS=feature_vals[17],
                    WEEKEND=feature_vals[18], )
                
                return FlightRequest(features=flight_input, true_delay=true_delay)
                
    raise HTTPException(
        status_code=500,
        detail="Row not found or CSV formatting issue on row. Try again.")

    