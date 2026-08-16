import psycopg
import os

conn = psycopg.connect(
    host="us-flight-delay-prediction-log.cdaaom8syj04.us-east-2.rds.amazonaws.com",
    port=5432,
    dbname="FlightDelayPredictionLog",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE prediction_logs (
            id BIGSERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            month INTEGER,
            op_unique_carrier VARCHAR(20),
            origin VARCHAR(20),
            dest VARCHAR(20),
            dep_delay_new INTEGER,
            dep_time_blk DOUBLE PRECISION,
            taxi_out DOUBLE PRECISION,
            cancelled DOUBLE PRECISION,
            diverted DOUBLE PRECISION,
            crs_elapsed_time DOUBLE PRECISION,
            distance DOUBLE PRECISION,
            carrier_delay DOUBLE PRECISION,
            weather_delay DOUBLE PRECISION,
            nas_delay DOUBLE PRECISION,
            security_delay DOUBLE PRECISION,
            late_aircraft_delay DOUBLE PRECISION,
            longest_add_gtime DOUBLE PRECISION,
            div_airport_landings DOUBLE PRECISION,
            weekend DOUBLE PRECISION,
            predicted_delay INTEGER,
            true_delay INTEGER
        );
    """)

conn.commit()
conn.close()