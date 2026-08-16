import pytest
import cleaning as clean
import pandas as pd 


def test_load_monthly_data():
    df = clean.load_monthly_data()
    assert list(df.columns) == ['MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK', 'OP_UNIQUE_CARRIER', 'ORIGIN',
           'DEST', 'DEP_DELAY_NEW', 'DEP_TIME_BLK', 'TAXI_OUT', 'ARR_DEL15',
           'CANCELLED', 'DIVERTED', 'CRS_ELAPSED_TIME', 'FLIGHTS', 'DISTANCE',
           'CARRIER_DELAY', 'WEATHER_DELAY', 'NAS_DELAY', 'SECURITY_DELAY',
           'LATE_AIRCRAFT_DELAY', 'LONGEST_ADD_GTIME', 'DIV_AIRPORT_LANDINGS',
           'DIV_ARR_DELAY']
    assert len(df) > 7000000
    

def test_create_weekend():
    df = pd.DataFrame({'DAY_OF_WEEK': [1, 5, 6, 7], 'DAY_OF_WEEK_NAME': ['Mon', 'Fri', 'Sat', 'Sun']})
    df = clean.create_weekend(df)
    assert df['WEEKEND'].tolist() == [0, 1, 1, 1]


def test_drop_unness_col():
    df = pd.DataFrame({'DAY_OF_MONTH': [3, 19, 26], 'FLIGHTS': [1, 1, 1], 'DAY_OF_WEEK': [1, 5, 7], 'WEEKEND': 
        [0, 1, 1], 'DEST': ['LAX', 'ATL', 'EUG']})
    df = clean.drop_unness_col(df)
    assert list(df.columns) == ['WEEKEND', 'DEST']

def test_adjust_time_block():
    df = pd.DataFrame({'DEP_TIME_BLK': ['12:00-12:59', '09:00-09:59', '01:00-01:59']})
    df = clean.adjust_time_block(df)
    assert df['DEP_TIME_BLK'].tolist() == ['12', '09', '01']

def test_fix_negatives():
    df = pd.DataFrame({'DEP_DELAY_NEW': [0, -3, 6] , 'CRS_ELAPSED_TIME': [-79, 24, 1076]})
    df = clean.fix_negatives(df)
    assert df['DEP_DELAY_NEW'].tolist() == [0, 0, 6]
    assert df['CRS_ELAPSED_TIME'].tolist() == [79, 24, 1076]

def test_fill_na():
    df = pd.DataFrame({'CRS_ELAPSED_TIME': [None, 60, 300], 'CARRIER_DELAY': [23, 0, None], 
        'WEATHER_DELAY': [0, None, 1], 'NAS_DELAY': [None, 5, 0], 'SECURITY_DELAY': [14, 0, None], 
        'LATE_AIRCRAFT_DELAY': [None, None, None], 'LONGEST_ADD_GTIME': [None, None, 11], 
        'TAXI_OUT': [None, 12, 3], 'DIV_AIRPORT_LANDINGS': [None, None, 3]})
    df = clean.fill_nan(df)
    assert df['CRS_ELAPSED_TIME'].tolist() == [180, 60, 300]
    assert df['CARRIER_DELAY'].tolist() == [23, 0, 0]
    assert df['WEATHER_DELAY'].tolist() == [0, 0, 1]
    assert df['NAS_DELAY'].tolist() == [0, 5, 0]
    assert df['SECURITY_DELAY'].tolist() == [14, 0, 0]
    assert df['LATE_AIRCRAFT_DELAY'].tolist() == [0, 0, 0]
    assert df['LONGEST_ADD_GTIME'].tolist() == [0, 0, 11]
    assert df['TAXI_OUT'].tolist() == [0, 12, 3]
    assert df['DIV_AIRPORT_LANDINGS'].tolist() == [0, 0, 3]

def test_fix_target_for_div_canc():
    df = pd.DataFrame({'ORIGIN': ['EUG', 'DEN', 'ORD', 'PDX'], 'DEST': ['DEN', 'PDX', 'TUS', 'DEN'], 
                       'DIV_ARR_DELAY': [35, 0, 0, 15], 'DIVERTED': [1, 0, 0, 0], 
                       'ARR_DEL15': [None, 0, None, 1], 'CANCELLED': [None, 0, 1, 0]}).reset_index()
    df = clean.fix_target_for_div_canc(df).sort_values('index')
    assert df['CANCELLED'].tolist() == [0, 0, 1, 0]
    assert df['ARR_DEL15'].tolist() == [1, 0, 1, 1]
    assert "DIV_ARR_DELAY" not in df.columns

def test_pre_encoding():
    df = pd.DataFrame({'MONTH': [3, 7, 12], 'OP_UNIQUE_CARRIER':['RTF', 'HBG', 'QSD'], 
                       'ORIGIN': ['DEN', 'ORD', 'PDX'], 'DEST': ['EUG', 'PDX', 'TUS'], 
                       'DEP_TIME_BLK': ['12', '09', '01'], 'SECURITY_DELAY': [17, '0', 45]})
    df = clean.pre_encoding(df)
    assert df['DEP_TIME_BLK'].tolist() == [12.0, 9.0, 1.0]
    assert df['SECURITY_DELAY'].tolist() == [17.0, 0.0, 45.0]
    assert list(df.columns) == ['MONTH', 'OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST', 'DEP_TIME_BLK', 
                                'SECURITY_DELAY']



