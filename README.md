## Overview
This repository contains a fully containerized, production ready, machine learning model system deployed on AWS. This system uses a model trained on U.S. flight data from the last year to predict if a flight will be delayed by more than 15 minutes. This system includes...

- Experiment Tracking Model Registry on Weights & Biases (https://wandb.ai/claire-coughran-university-of-denver/U.S.%20Flight%20Delay%20Prediction?nw=nwuserclairecoughran)
    - Model is encoded using OneHotEncoder()
    - Model trained using scikit-learn LogisticRegression()
    - All models are logged to Weight & Biases with coefficents, intercept, model parameters, and performance
      metrics.
    - The best model log_reg_v5 was promoted to production
- FastAPI Backend (http://localhost:8000/)
    - Loads the log_reg_v5 model
    - /root: {"Hello": "World"}
    - /health: {"status": "ok"}
    - /predict: Uses the model to predict given a complete request body (see ex below) and logs the
      prediction into AWS RDS database (see more below) with all the feature values and true delay. 
    - /example: Finds a single random row picked from the entire clean dataset and returns formats as request
      body.
- AWS RDS ()
    - All feature values of the flight
    - Timestamp
    - Predicted Delay
    - True Delay
    - Total Prediction Runtime
- User Interface Frontend (http://localhost:8501/)
    - Streamlit app with questions and entry fields to make sending prediction requests easy.
- Model Monitoring Dashboard (http://localhost:8502/)
    - Pulls the data from the AWS RWD log database
    - Presents accuracy, target drift analysis, prediction latency over time, and route reliability between
      airports 
- CI/CD Testing Pipeline using GitHub Actions ()
    - test_cleaning.py: Unit tests for various cleaning tasks. 
    - test_train.py: Unit tests for various training and W&B logging.
    - test_app.py: Unit test on function to load model and integration test on endpoints.
    - test_frontend.py: Unit test on function to get AWS RDS log database and integraion test to test
      streamlit sends request body correctly.
    - ci.yml: Defines workflow for testing

## Structure
final project

    |-.github
    
    |    |-workflows
    
    |    |    |-ci.yml
    
    |-phase 1
    
    |    |-requirements.txt
    
    |    |-cleaning
    
    |    |    |-cleaning.py
    
    |    |    |-test_cleaning.py
    
    |    |    |-monthly data
    
    |    |        |-apr_26_airline.csv
    
    |    |        |-aug_25_airline.csv
    
    |    |        |-...
    
    |    |        |-sep_25_airline.csv
    
    |    |-training    
    
    |         |-train.py
    
    |         |-test_train.py
    
    |-phase 2   
    
    |    |-app.py
    
    |    |-clean_delays.csv
    
    |    |-create_database.py
    
    |    |-requirements.txt
    
    |    |-test_app.py
    
    |-phase 3
    
    |    |-user_interface.py
    
    |    |-dashboard.py
    
    |    |-airport_codes.csv
    
    |    |-requirements.txt
    
    |    |-test_frontend.py
    
    |-.gitattributes
    
    |-.gitignore
    
    |-README.md

            
## Instructions to Run Locally
1. Clone repository
   
2. Navigate to project directory

3. In terminal set weights and biases key using

  ```powershell
  $env:WANDB_API_KEY="YOUR_WANDB_API_KEY"
  ```
    and the datbase password using
   
   ```powershell 
    $env:DB_PASSWORD=*password*
    ```
   
4. Run

   ```powershell
   make build
   ```

5. Run
   
   ```powershell
   make run
   ```
   
6. Open the fastapi backend at http://localhost:8000/

7. Open the user interface at http://localhost:8501/

8. Open the monitoring dashboard at http://localhost:8502/

9. When done run

    ```powershell
    make clean
    ```

## AWS Deployment
# 1. Create the EC2 Instances

    Create two EC2 instances:
    
    * `flight-api` — Backend
    * `flight-frontend` — Frontend
    
    Install/use **Amazon Linux 2023** for both.
    
    Configure the security groups:
    
    **Backend**
    
    * SSH: `22`
    * FastAPI: `8000`
    
    **Frontend**
    
    * SSH: `22`
    * Streamlit: `8501`
    * Streamlit: `8502`
    
    In the AWS RDS database, use **Set up EC2 connection** to add connections for:
    
    * `flight-api`
    * `flight-frontend`


# 2. Deploy the Backend

    On your local computer, navigate to the folder containing `fastapi-key.pem`.
    
    Connect to the backend:
    
    ```powershell
    ssh -i "fastapi-key.pem" ec2-user@ec2-18-222-25-213.us-east-2.compute.amazonaws.com
    ```
    
    Install and configure Docker and Git:
    
    ```bash
    sudo dnf update -y
    sudo dnf install -y docker git git-lfs
    sudo systemctl enable --now docker
    sudo usermod -aG docker ec2-user
    ```
    
    Log out so the Docker group change takes effect:
    
    ```bash
    exit
    ```
    
    Reconnect:
    
    ```powershell
    ssh -i "fastapi-key.pem" ec2-user@ec2-18-222-25-213.us-east-2.compute.amazonaws.com
    ```
    
    Set environment variables:
    
    ```bash
    export WANDB_API_KEY="YOUR_WANDB_API_KEY"
    export DB_PASSWORD="YOUR_DATABASE_PASSWORD"
    ```
    
    Clone the project:
    
    ```bash
    git clone https://github.com/clairecoughran/End-to-End-Machine-Learning-Application.git
    cd End-to-End-Machine-Learning-Application
    ```
    
    Download the Git LFS files **before building the image**:
    
    ```bash
    git lfs install
    git lfs pull
    ```
    
    Build and run the backend:
    
    ```bash
    docker build -t flight-api "./phase 2"
    
    docker run -d \
      --name flight-api-container \
      --restart unless-stopped \
      -p 8000:8000 \
      -e WANDB_API_KEY="$WANDB_API_KEY" \
      -e DB_PASSWORD="$DB_PASSWORD" \
      flight-api
    ```
    


# 3. Deploy the Frontend

    Open a **new local terminal** and navigate to the folder containing `fastapi-key.pem`.
    
    Connect to the frontend:
    
    ```powershell
    ssh -i "fastapi-key.pem" ec2-user@ec2-16-59-60-130.us-east-2.compute.amazonaws.com
    ```
    
    Install and configure Docker and Git:
    
    ```bash
    sudo dnf update -y
    sudo dnf install -y docker git git-lfs
    sudo systemctl enable --now docker
    sudo usermod -aG docker ec2-user
    ```
    
    Log out:
    
    ```bash
    exit
    ```
    
    Reconnect:
    
    ```powershell
    ssh -i "fastapi-key.pem" ec2-user@ec2-16-59-60-130.us-east-2.compute.amazonaws.com
    ```
    
    Set the database password:
    
    ```bash
    export DB_PASSWORD="YOUR_DATABASE_PASSWORD"
    ```
    
    Clone the project:
    
    ```bash
    git clone https://github.com/clairecoughran/End-to-End-Machine-Learning-Application.git
    cd End-to-End-Machine-Learning-Application
    ```
    
    Download the Git LFS files **before building the image**:
    
    ```bash
    git lfs install
    git lfs pull
    ```
    
    Build and run the frontend:
    
    ```bash
    docker build -t flight-frontend "./phase 3"
    
    docker run -d \
      --name flight-frontend-container \
      --restart unless-stopped \
      -p 8501:8501 \
      -p 8502:8502 \
      -e API_URL="http://18.222.25.213:8000" \
      -e DB_PASSWORD="$DB_PASSWORD" \
      flight-frontend
    ```


# 4. Verify Deployment

    Backend:
    
    ```text
    http://18.222.25.213:8000/docs
    ```
    
    Prediction interface:
    
    ```text
    http://16.59.60.130:8501
    ```
    
    Monitoring dashboard:
    
    ```text
    http://16.59.60.130:8502
    ```
    
    Verify both containers:
    
    **Backend:**
    
    ```bash
    docker ps
    ```
    
    **Frontend:**
    
    ```bash
    docker ps
    ```
    
    Both containers use `--restart unless-stopped`, and Docker was enabled with `systemctl enable --now docker`, so the applications will restart automatically after an EC2 reboot.

# 5. Restart and Verification

    **Backend EC2**
    
    Set the backend container restart policy:
    
    ```bash
    docker update --restart unless-stopped flight-api-container
    ```
    
    Enable Docker to start automatically after EC2 reboot:
    
    ```bash
    sudo systemctl enable docker
    ```
    
    Verify the restart policy:
    
    ```bash
    docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' flight-api-container
    ```
    
    Expected output:
    
    ```text
    unless-stopped
    ```
    
    **Frontend EC2**
    
    Set the frontend container restart policy:
    
    ```bash
    docker update --restart unless-stopped flight-frontend-container
    ```
    
    Enable Docker to start automatically after EC2 reboot:
    
    ```bash
    sudo systemctl enable docker
    ```
    
    Verify the restart policy:
    
    ```bash
    docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' flight-frontend-container
    ```
    
    Expected output:
    
    ```text
    unless-stopped
    ```
    

# 6. Future Use 
    Backend:
    ```powershell
    ssh -i "fastapi-key.pem" ec2-user@ec2-18-222-25-213.us-east-2.compute.amazonaws.com
    ```
    
    Frontend: 
    ```powershell
    ssh -i "fastapi-key.pem" ec2-user@ec2-16-59-60-130.us-east-2.compute.amazonaws.com
    ```




# Request Body 
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



# curl Example
Prediction:
    curl -X 'POST' \
      'http://localhost:8000/predict' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "features": {
        "MONTH": 1,
        "OP_UNIQUE_CARRIER": "WN",
        "ORIGIN": "AUS",
        "DEST": "DEN",
        "DEP_DELAY_NEW": 14,
        "DEP_TIME_BLK": 43,
        "TAXI_OUT": 9,
        "CANCELLED": 0,
        "DIVERTED": 0,
        "CRS_ELAPSED_TIME": 140,
        "DISTANCE": 775,
        "CARRIER_DELAY": 0,
        "WEATHER_DELAY": 0,
        "NAS_DELAY": 0,
        "SECURITY_DELAY": 0,
        "LATE_AIRCRAFT_DELAY": 18,
        "LONGEST_ADD_GTIME": 0,
        "DIV_AIRPORT_LANDINGS": 0,
        "WEEKEND": 0
      },
      "true_delay": 1
    }'

Response:
    {
      "delay": 1
    }