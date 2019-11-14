from boto import kinesis
import time
import json
from csv import writer
from csv import QUOTE_MINIMAL

from boto.kinesis.exceptions import ExpiredIteratorException

import threading
from influxdb import InfluxDBClient
from datetime import datetime

class KinesisConsumerInflux():

    def __init__(self,outputdata=[],ip="192.168.33.10",port="8086",db="cardata",kinesis_stream ="average_km_per_period" ):

        self.kinesis = kinesis.connect_to_region("eu-west-1")
        self.outputdata = outputdata

        try:
            self.client = InfluxDBClient(host=ip, port=int(port))

        except Exception as e:
            print("Could not establish connection or wrong params for influx. Error: {}".format(str(e)))

        db_found = False



        for elem in self.client.get_list_database():
            if elem["name"] == db:
                db_found = True
        if not db_found:
            print("Target DB not yet existing. Attempting to create")
            self.client.create_database(db)


        self.client.switch_database(db)

        self.kinesis_stream = kinesis_stream

        self.queue = []




    def iterate_shards(self,shard_ids):
        for value in shard_ids:  # Iterate over all shards and obtain the data
            out = self.kinesis.get_records(value["shard_iterator"], limit=100)

            for o in out["Records"]:  # Process data record-wise

                dictionary = json.loads(o["Data"])

                timestamp = time.time()
                time_date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                datatowrite = []

                measurement = {"measurement": self.kinesis_stream, "time": time_date, "fields": {}, "tags": {}}

                for key, value in dictionary.items():
                    val_to_write = value
                    if type(value) == int:
                        val_to_write = float(value)
                    if not key == "id":
                        measurement["fields"][key] = val_to_write
                    else:
                        measurement["tags"][key] = val_to_write



                self.client.write_points([measurement])
                time.sleep(0.1)

    def readToInflux(self):
        print("Starting Stream collection for {}".format(self.kinesis_stream))

        response = self.kinesis.describe_stream(self.kinesis_stream)
        shard_ids = []

        # Obtain all shard iterators
        if response and 'StreamDescription' in response:
            stream_name = response['StreamDescription']['StreamName']
            for shard_id in response['StreamDescription']['Shards']:
                shard_id = shard_id['ShardId']
                shard_iterator = self.kinesis.get_shard_iterator(stream_name, shard_id, "LATEST")
                shard_ids.append({'shard_id': shard_id, 'shard_iterator': shard_iterator['ShardIterator']})



        while True:
            try:

                self.iterate_shards(shard_ids)


            except ExpiredIteratorException as e:
                # When the shard iterator expires, create a new one
                print("Iterator expired. This is expected. Creating a new one.")
                response = self.kinesis.describe_stream(self.kinesis_stream)
                shard_ids = []

                # Obtain all shard iterators
                if response and 'StreamDescription' in response:
                    stream_name = response['StreamDescription']['StreamName']
                    for shard_id in response['StreamDescription']['Shards']:
                        shard_id = shard_id['ShardId']
                        shard_iterator = self.kinesis.get_shard_iterator(stream_name, shard_id, "LATEST")
                        shard_ids.append({'shard_id': shard_id, 'shard_iterator': shard_iterator['ShardIterator']})

                self.iterate_shards(shard_ids)

            except Exception as e:
                print(str(e))
                print("Trying to continue")


import sys
arguments = sys.argv[1:]

if len(arguments) > 1:
    for elem in arguments:
        results = []
        consumer = KinesisConsumerInflux(outputdata=[], kinesis_stream=elem)
        thread = threading.Thread(target=consumer.readToInflux, args=())
        thread.start()


else:
    print("No arguments given. Please state the names of the kinesis streams you want to observe")

