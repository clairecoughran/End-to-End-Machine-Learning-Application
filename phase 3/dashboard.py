import psycopg
import pandas as pd
import os
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import streamlit as st


def get_log():
    conn = psycopg.connect(
        host="us-flight-delay-prediction-log.cdaaom8syj04.us-east-2.rds.amazonaws.com",
        port=5432,
        dbname="FlightDelayPredictionLog",
        user="postgres",
        password=os.getenv("DB_PASSWORD"))
    
    with conn.cursor() as cur:
        query = "SELECT * FROM prediction_logs"
        df = pd.read_sql(query, conn)
    
    conn.close()
    return df

def main():
    df = get_log()
    
    # --- App Header ---
    ## Title
    st.title('U.S. Flight Delay Prediction Monitoring Dashboard')
    
    ## Short Description 
    st.write('This dashboard monitors the perfomance of a logictically trained model that predicts U.S. flight data. ')
    
    # --- Dashboard ---
    # ACCURACY
    accuracy = (df["predicted_delay"] == df["true_delay"]).mean()
    st.subheader("Accuracy: " + str(accuracy))
    
    
    # TARGET DRIFT ANALYSIS
    df_counts = pd.DataFrame(df["predicted_delay"].value_counts()).reset_index()
    df_counts.columns = ["predicted_delay", "count"]
    
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    
    sns.barplot(data=df_counts, x="predicted_delay", y="count", hue="predicted_delay", 
                palette=["#1f77b4", "skyblue"], ax=ax1)
    
    ax1.legend_.remove()
    ax1.set_ylabel("Count of Predicted Values")
    ax1.set_xlabel("Predicted Delay")
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["No", "Yes"])
    ax1.set_title("Target Drift Analysis")
    
    st.pyplot(fig1)
    
    
    # PREDICTION LATENCY
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    
    sns.lineplot(data=df, x="id", y="prediction_latency", color="blue", ax=ax2)
    
    ax2.set_xticks(np.arange(5, len(df), 100))
    ax2.set_ylabel("Prediction Latency (seconds)")
    ax2.set_xlabel("Prediction Run")
    ax2.set_title("Prediction Latency Over Time", fontsize=12)
    
    st.pyplot(fig2)
    
    # ROUTE RELIABILITY
    df2 = df[['origin', 'dest', 'true_delay']]
    df2["route"] = df2["origin"] + "_" + df2["dest"]
    
    origin = st.selectbox("Select origin:", df2["origin"].unique())
    dest = st.selectbox("Select destination:", df2["dest"].unique())
    route = origin + "_" + dest
    
    route_reliability = df2[df2["route"] == route]['true_delay'].mean()
    origin_reliability = df2[df2["origin"] == origin]['true_delay'].mean()
    dest_reliability = df2[df2["dest"] == dest]['true_delay'].mean()
    
    st.subheader("Route Reliability")
    st.write("The proportion of flights with an arrival delay from " + origin + " to " + dest + " is " + str(route_reliability)+ ".")
    
    st.write("The proportion of flights with an arrival delay coming from " + origin + " is " + str(origin_reliability) + ".")
    
    st.write("The proportion of flights with an arrival delay going to " + dest + " is " + str(dest_reliability) + ".")


if __name__ == "__main__":
    main()



