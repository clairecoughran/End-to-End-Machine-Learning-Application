import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import joblib
import wandb
import os

def read_in_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', '..', 'phase 2', 'clean_delays.csv'))
    columns = ['MONTH', 'OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST', 'DEP_DELAY_NEW',
            'DEP_TIME_BLK', 'TAXI_OUT', 'ARR_DEL15', 'CANCELLED', 'DIVERTED',
            'CRS_ELAPSED_TIME', 'DISTANCE', 'CARRIER_DELAY', 'WEATHER_DELAY',
            'NAS_DELAY', 'SECURITY_DELAY', 'LATE_AIRCRAFT_DELAY',
            'LONGEST_ADD_GTIME', 'DIV_AIRPORT_LANDINGS', 'WEEKEND']
    return df[columns]

def train_test(delays):
    X = delays.drop('ARR_DEL15', axis=1)
    y = delays['ARR_DEL15']
    return train_test_split(X, y, test_size=0.3, stratify=y, random_state=14)

def create_preprocesser():
    cat_feats = ['MONTH', 'OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST', 'DEP_TIME_BLK']
    return ColumnTransformer(transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), cat_feats)], remainder="passthrough")

def calc_performance(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    if precision + recall == 0: f1 = 0
    else: f1 = 2 * (precision * recall) / (precision + recall)
    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}

delays = read_in_data()
X_train, X_test, y_train, y_test = train_test(delays)
preprocess = create_preprocesser()

def train_model(model_name, p='deprecated', c=1.0, l1=0.0, d=False, t=0.0001, fit_i=True, int_scale=1, cw=None, s='lbfgs', max_i=100, v=0):

    model_pkl = model_name + ".pkl"
    
    # configure and train model
    pipe = Pipeline([("preprocess", preprocess),
                    ("model", LogisticRegression(
                        penalty=p, C=c, l1_ratio=l1, dual=d, tol=t,
                        fit_intercept=fit_i, intercept_scaling=int_scale,
                        class_weight=cw, random_state=14, solver=s,
                        max_iter=max_i, verbose=v))])

    pipe.fit(X_train, y_train)
    
    # save model for 
    model_path = "models/" + model_pkl
    joblib.dump(pipe, model_path)

    pipe_model = pipe.named_steps["model"]
    
    parameters = pipe_model.get_params()
    
    # configure wanb model
    run = wandb.init(
        # Set the wandb entity where your project will be logged (generally your team name).
        entity="claire-coughran-university-of-denver",
        # Set the wandb project where this run will be logged.
        project="U.S. Flight Delay Prediction",
        # Track hyperparameters and run metadata.
        config={ 
            "model": model_name,
            "dataset": "U.S. DOT/BTS On-Time Performance",
            "coefficents": pipe_model.coef_, 
            "intercept": pipe_model.intercept_,
            "C": parameters['C'],
            "penalty": parameters['penalty'],
            "solver": parameters['solver'],
            "max_iterations": parameters['max_iter'], 
            "random_state": 14},)

    # calculate performace of wanb model
    y_pred = pipe.predict(X=X_test)
    perf_dict = calc_performance(y_test, y_pred)
    
    # log performance of wanb model
    run.log(perf_dict)
    print(model_name)
    print(perf_dict)
    
    # Save your trained models as artifacts within your experiment tracking tool.
    artifact = wandb.Artifact(name=model_name, type="model")
    artifact.add_file(model_path)
    wandb.log_artifact(artifact)
    return 

#train_model('log_reg_v0')

#train_model('log_reg_v1', s='sag')

#train_model('log_reg_v2', s='saga')

#train_model('log_reg_v3', p='l2')

#train_model('log_reg_v4', c=0.1 )

#train_model('log_reg_v5', c=100)

#train_model('log_reg_v6', c=10)

#train_model('log_reg_v7', c=100, max_i=50)

#train_model('log_reg_v8', c=100, max_i=75)