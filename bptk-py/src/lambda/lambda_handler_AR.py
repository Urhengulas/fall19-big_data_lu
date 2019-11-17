from __future__ import print_function

import json
from statsmodels.tsa.ar_model import AR
from boto import kinesis
import time
import base64

def setup_kinesis(stream_name,region="eu-west-1"):
    ## Create stream if not already existing
    kin = kinesis.connect_to_region(region)

    if not stream_name in kin.list_streams()['StreamNames']:
        kin.create_stream(stream_name, 1)
        kin.describe_stream(stream_name)
        time.sleep(10)

    return kin




def process_records(records,target_stream, column="capacity",id=1,horizon=100):

    ####################################
    ########## PREPROCESSING ###########
    ####################################

    data = []
    start_index = None
    last_index = None

    # Prepare Data
    if len(records) > 0:

        # Find first and last time element for given ID
        for o in list(reversed(records)):

            encoded =  o['kinesis']['data']
            dictionary = eval(base64.b64decode(encoded)) # Should be my dic!

            if dictionary['id'] == id:
                last_index = dictionary['time']
                break

        # Find first time we observe an item for given ID
        for o in records:
            encoded = o['kinesis']['data']
            dictionary = eval(base64.b64decode(encoded))

            if dictionary['id'] == id:
                if not start_index:
                    start_index = dictionary['time']

                # Add data to the dictionary
                data += [dictionary[column]]

    #################################
    ########## PREDICTION ###########
    #################################

    # Predict if we found data for the given ID
    if len(data) > 0:

        # make prediction
        try:
            model = AR(data)
            # fit model
            model_fit = model.fit()
            if len(data) < horizon:
                horizon = len(data)
            prediction = model_fit.predict(len(data), len(data) + horizon)

            kin = setup_kinesis(target_stream)

            records = []
            for elem in prediction:
                last_index += 1
                records += [{'Data': json.dumps({"time": last_index,"prediction_" + column : elem,"id" : id}), 'PartitionKey': str(hash(id))}]

            kin.put_records(records, target_stream)
        except Exception as e:
            print(str(e))




def lambda_handler(event, context):
    for id in range(0,10):
        process_records(event["Records"],target_stream="AutoRegressive_car_ABM",id=id,horizon=100)

        return json.dumps({"Status": 200})

