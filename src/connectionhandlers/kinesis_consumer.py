from boto import kinesis
import time
import json
from csv import writer
from csv import QUOTE_MINIMAL
import pandas as pd
import threading


class KinesisConsumer():

    def __init__(self,outputdata=[]):

        self.kinesis = kinesis.connect_to_region("eu-west-1")
        self.outputdata = outputdata



    def readToCSV(self):
        print("Starting Stream collection")
        column_names = None
        outfile = open("stream.csv","a",encoding="UTF-8")
        csv_writer = writer(outfile, delimiter=';',
                            quotechar='|', quoting=QUOTE_MINIMAL)
        shard_id = 'shardId-000000000000'  # we only have one shard!  "average_km_per_period","sliding_average_km_until_charge"
        shard_it = self.kinesis.get_shard_iterator("MovingAverage_car_ABM", shard_id, "LATEST")["ShardIterator"]

        while True:

            out = self.kinesis.get_records(shard_it, limit=1000)
            shard_it = out["NextShardIterator"]

            for o in out["Records"]:
                if not column_names:
                    column_names = list(json.loads(o["Data"]).keys())
                    csv_writer.writerow(column_names)
                dictionary = json.loads(o["Data"])
                print(dictionary)
                self.outputdata = self.outputdata + [dictionary]

                csv_writer.writerow(list(dictionary.values()))
            outfile.flush()

            time.sleep(10)



    def readToPD(self):
        print("Starting Stream collection")
        shard_id = 'shardId-000000000000'  # we only have one shard!  "average_km_per_period","sliding_average_km_until_charge"
        shard_it = self.kinesis.get_shard_iterator("MovingAverage_car_ABM", shard_id, "TRIM_HORIZON")["ShardIterator"]
        data = {}
        while True:

            out = self.kinesis.get_records(shard_it, limit=10)
            shard_it = out["NextShardIterator"]
            key = "charge"
            id = 0
            for o in out["Records"]:
                dictionary = json.loads(o["Data"])


                if dictionary["id"] == id:

                    if key in data.keys():
                        data[key].update({dictionary["time"] : dictionary[key]})
                    else:
                        data[key] = {dictionary["time"] : dictionary[key]}

                    if "id" in data.keys():
                        data["id"].update({dictionary["time"]: dictionary["id"]})
                    else:
                        data["id"] = {dictionary["time"]: dictionary["id"]}

            df = pd.DataFrame(data)

            time.sleep(10)

results = []
consumer = KinesisConsumer(outputdata=results)

thread = threading.Thread(target=consumer.readToCSV,args=())
thread.start()


