import streamlit as st
import joblib
import pandas as pd
import wandb
import requests
import os

# ---Prep Work---
# maps airlines to there codes
airline_mapping = {
    'American Airlines': 'AA',
    'Alaska Airlines': 'AS',
    'JetBlue Airways': 'B6',
    'Delta Air Lines': 'DL',
    'Frontier Airlines': 'F9',
    'Allegiant Air': 'G4',
    'GoJet Airlines/United Express': 'G7',
    'Envoy Air': 'MQ',
    'SkyWest Airlines Inc.': 'OO',
    'United Air Lines': 'UA',
    'Southwest Airlines': 'WN',
    'Mesa Airlines Inc.': 'YV',
    'Republic Airline': 'YX',
    'Horizon Air': 'QX',
    'PSA Airlines': 'OH',
    'Piedmont Airlines': 'PT',
    'Endeavor Air': '9E',
    'CommuteAir': 'C5',
    'Spirit Air Lines': 'NK',
    'Hawaiian Airlines': 'HA'}

# maps yes/no to binary output
binary_mapping = {'Yes': 1, 'No': 0}

# used to map dest and origin from airport name to code 
airport_codes = pd.read_csv("airport_codes.csv")


# --- App Header ---
## Title
st.title('U.S. Flight Delay Prediction')


## Short Description 
st.markdown('This app ask several questions about pre-arrival flight information then will predict if the arrival time will be delayed by more than 15 minutes. The prediction is done using a logistic regression model that encodes categorical variables. ')

# --- Load the model ---
@st.cache_data    # ensures the model is loaded only once when the app starts
def load_model():
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

model = load_model()

# --- User input --- 
# MONTH
month = st.selectbox("What month is the flight taking off? (Ex: January=1, December=12)",
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

# OP_UNIQUE_CARRIER
airline_name = st.selectbox("What airline is the flight on?", list(airline_mapping.keys()), key='airline_select')
airline = airline_mapping[airline_name]

# ORIGIN
origin_full = st.selectbox("Where is your flight taking off from?", airport_codes['Description'].to_list(), key='origin_select')
origin = airport_codes.loc[airport_codes['Description'] == origin_full, 'Code'].iloc[0]


# DEST
dest_full = st.selectbox("Where is your flight taking off from?", airport_codes['Description'].to_list(), key='dest_select')
dest = airport_codes.loc[airport_codes['Description'] == origin_full, 'Code'].iloc[0]

# DEP_TIME_BLK
dep_time = float(st.number_input("What hour of the day was your flight scheduled to takeoff?"))

# DEP_DELAY_NEW
dep_delay_min = int(st.number_input("How many minutes after the scheduled takeoff did you takeoff?"))

# TAXI_OUT
taxi = float(st.number_input("How long did it take the plane to taxi to the runway?"))

# CANCELLED
cancelled_str = st.selectbox("Has the flight been cancelled?", list(binary_mapping.keys()), key='canc_select')
cancelled = float(binary_mapping[cancelled_str])
                            
# DIVERTED
diverted_str = st.selectbox("Has the flight been diverted?", list(binary_mapping.keys()), key='div_select')
diverted = float(binary_mapping[diverted_str])

# CRS_ELAPSED_TIME
flight_time = float(st.number_input("What was the length (in minutes) of the original scheduled flight?"))

# DISTANCE
flight_dist = float(st.number_input("What was the length (in miles) between the origin and destination?"))

# CARRIER_DELAY
carrier_delay = float(st.number_input("How many minutes of the delay were spent on a carrier delay"))

# WEATHER_DELAY
weather_delay = float(st.number_input("How many minutes of the delay were spent on a weather delay"))

# NAS_DELAY
nas_delay = float(st.number_input("How many minutes of the delay were spent on a national air system delay"))

# SECURITY_DELAY
security_delay = float(st.number_input("How many minutes of the delay were spent on a security delay"))

# LATE_AIRCRAFT_DELAY
late_plane_delay = float(st.number_input("How many minutes of the delay were spent on a late aircraft delay"))

# LONGEST_ADD_GTIME
gtime = float(st.number_input("If your plane returned to the gate after leaving, how long was the longest time spent before returning "))

# DIV_AIRPORT_LANDINGS
diversions = float(st.number_input("How many airport have you been diverted to?"))

# WEEKEND
weekend_str = st.selectbox("Is the flight on a weekend (Friday-Sunday)?", list(binary_mapping.keys()), key='weekend_select')
weekend = float(binary_mapping[weekend_str])

# true_delay
true_delay_str = st.selectbox("Did your flight end up arriving more than 15 minutes after the scheduled time?", list(binary_mapping.keys()), key='true_select')
true_delay = float(binary_mapping[true_delay_str])

# format for request 
request_body = {"features": {
                    "MONTH":month,
                    "OP_UNIQUE_CARRIER":airline,
                    "ORIGIN":origin,
                    "DEST":dest,
                    "DEP_DELAY_NEW":dep_delay_min,
                    "DEP_TIME_BLK":dep_time,
                    "TAXI_OUT":taxi,
                    "CANCELLED":cancelled,
                    "DIVERTED":diverted,
                    "CRS_ELAPSED_TIME":flight_time,
                    "DISTANCE":flight_dist,
                    "CARRIER_DELAY":carrier_delay,
                    "WEATHER_DELAY":weather_delay,
                    "NAS_DELAY":nas_delay,
                    "SECURITY_DELAY":security_delay,
                    "LATE_AIRCRAFT_DELAY":late_plane_delay,
                    "LONGEST_ADD_GTIME":gtime,
                    "DIV_AIRPORT_LANDINGS":diversions,
                    "WEEKEND":weekend}, 
                "true_delay": true_delay}

# --- Make prediction ---
if st.button('Analyze'):
    response = requests.post("http://localhost:8000/predict", json=request_body)
    prediction = response.json()["delay"]
    
    if prediction == 1: 
        st.success("Your flight is not predicted to be delayed arriving at your destination!")
    else: 
        st.error("Your flight is predicted to be delayed arriving at your destination.")

