import train 
import pytest
import pandas as pd 
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder


def test_read_in_data():
    df = train.read_in_data()
    assert list(df.columns) == ['MONTH', 'OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST', 'DEP_DELAY_NEW',
       'DEP_TIME_BLK', 'TAXI_OUT', 'ARR_DEL15', 'CANCELLED', 'DIVERTED',
       'CRS_ELAPSED_TIME', 'DISTANCE', 'CARRIER_DELAY', 'WEATHER_DELAY',
       'NAS_DELAY', 'SECURITY_DELAY', 'LATE_AIRCRAFT_DELAY',
       'LONGEST_ADD_GTIME', 'DIV_AIRPORT_LANDINGS', 'WEEKEND']

def test_train_test_split():
    df = pd.DataFrame({'x0': [2, 5, 8, 10], 'x1': [1, 9, 5, 4], 'ARR_DEL15': [1, 0, 1, 0]})
    X_train, X_test, y_train, y_test = train.train_test(df)
    assert len(X_train) == len(y_train)
    assert len(X_test) == len(y_test)

def test_create_preprocesser_structure():
    pre = train.create_preprocesser()
    assert isinstance(pre, ColumnTransformer)
    assert isinstance(pre.transformers[0][1], OneHotEncoder)
    assert pre.transformers[0][2] == ['MONTH', 'OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST', 'DEP_TIME_BLK']

def test_calc_performance():
    y_true = [0, 1, 0, 1, 1, 0, 1, 0, 0, 1] 
    y_pred = [1, 1, 0, 1, 1, 0, 1, 0, 0, 1] 
    perf = train.calc_performance(y_true, y_pred)
    assert perf["accuracy"] == pytest.approx(0.9)
    assert perf["precision"] == pytest.approx(0.83333, abs=1e-4)
    assert perf["recall"] == pytest.approx(1.0)
    assert perf["f1"] == pytest.approx(0.9090, abs=1e-4)








    