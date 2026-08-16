import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from scipy.sparse import hstack
import joblib
import numpy as np

def load_monthly_data():
    month_codes = ['jan_26', 'feb_26', 'mar_26', 'apr_26', 'may_26', 'jun_26', 'jul_25', 'aug_25', 'sep_25', 
                   'oct_25', 'nov_25', 'dec_25'] 

    delays = pd.DataFrame(columns=['MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK', 'OP_UNIQUE_CARRIER', 'ORIGIN',
           'DEST', 'DEP_DELAY_NEW', 'DEP_TIME_BLK', 'TAXI_OUT', 'ARR_DEL15',
           'CANCELLED', 'DIVERTED', 'CRS_ELAPSED_TIME', 'FLIGHTS', 'DISTANCE',
           'CARRIER_DELAY', 'WEATHER_DELAY', 'NAS_DELAY', 'SECURITY_DELAY',
           'LATE_AIRCRAFT_DELAY', 'LONGEST_ADD_GTIME', 'DIV_AIRPORT_LANDINGS',
           'DIV_ARR_DELAY'])

    for month in month_codes:
        df = pd.read_csv('monthly data/' + month + '_airline.csv')
        if 'DEP_DELAY' in df.columns: 
            df['DEP_DELAY_NEW'] = df['DEP_DELAY']
            df = df.drop('DEP_DELAY', axis=1)
        delays = pd.concat([delays, df])
    return delays

    
def create_weekend(delays): 
    # instead of encoding a variable for each day of the week add a 
    delays['WEEKEND'] = [1 if x>4 else 0 for x in delays['DAY_OF_WEEK']]
    return delays
    
def drop_unness_col(delays):
    return delays.drop(['DAY_OF_MONTH', 'FLIGHTS', 'DAY_OF_WEEK'], axis=1)
    
def adjust_time_block(delays):
    delays['DEP_TIME_BLK']= delays['DEP_TIME_BLK'].str[:2]
    return delays

def fix_negatives(delays):
    delays['DEP_DELAY_NEW'] = [x if x>0 else 0 for x in delays['DEP_DELAY_NEW']]
    delays['CRS_ELAPSED_TIME'] = [x if x>0 else -x for x in delays['CRS_ELAPSED_TIME']]
    return delays 

def fill_nan(delays):
    # fill with mean
    delays['CRS_ELAPSED_TIME']  = delays['CRS_ELAPSED_TIME'].fillna(np.mean(delays['CRS_ELAPSED_TIME']))

    # fill with 0
    fill0 = delays[['CARRIER_DELAY', 'WEATHER_DELAY', 'NAS_DELAY', 'SECURITY_DELAY','LATE_AIRCRAFT_DELAY', 
                    'LONGEST_ADD_GTIME', 'TAXI_OUT', 'DIV_AIRPORT_LANDINGS']]
    fill0 = fill0.fillna(0)
    delays[['CARRIER_DELAY', 'WEATHER_DELAY', 'NAS_DELAY', 'SECURITY_DELAY','LATE_AIRCRAFT_DELAY', 
            'LONGEST_ADD_GTIME', 'TAXI_OUT', 'DIV_AIRPORT_LANDINGS']] = fill0

    return delays 

def fix_target_for_div_canc(delays):
    diverted = delays[delays['DIVERTED'] == 1]
    not_diverted = delays[delays['DIVERTED'] == 0]

    # ARR_DEL15 is null for diverted routes so set ARR_DEL_15 by filtering DIV_ARR_DELAY  
    diverted['ARR_DEL15'] = [1 if x>15 else 0 for x in diverted['DIV_ARR_DELAY']]
    # Fill Nan with 0
    diverted['CANCELLED'] = diverted['CANCELLED'].fillna(0)
    # If not diverted then even if delayed this is 0 
    not_diverted['DIV_ARR_DELAY'] = not_diverted['DIV_ARR_DELAY'].fillna(0)

    # Nan exists still for non diverted 
    cancelled = not_diverted[not_diverted['CANCELLED'] == 1]
    # If cancelled then arrival never happens so delay is >15
    cancelled['ARR_DEL15'] = cancelled['ARR_DEL15'].fillna(1)
    # One case of nan delay value for not cancelled or diverted route drop since only one case 
    not_cancelled = not_diverted[not_diverted['CANCELLED'] == 0].fillna(0)

    # concat diverted and cancelled and not cancelled
    return pd.concat([diverted, not_cancelled, cancelled], ignore_index=True).drop('DIV_ARR_DELAY', axis=1)

def pre_encoding(delays):
    # prepare for encoding that will be done in pipeline
    cat_feats = ['MONTH', 'OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST']
    cat_data = delays[cat_feats]
    num_data = delays.drop(cat_feats, axis=1)
    num_data = num_data.apply(pd.to_numeric, errors='coerce').astype('float32')
    
    return pd.concat([cat_data, num_data], axis=1)

delays = load_monthly_data()
delays = create_weekend(delays)
delays = drop_unness_col(delays)
delays = adjust_time_block(delays)
delays = fix_negatives(delays)
delays = fill_nan(delays)
delays = fix_target_for_div_canc(delays)
delays = pre_encoding(delays)

#save dataframe
delays.to_csv("clean_delays.csv", index=False)