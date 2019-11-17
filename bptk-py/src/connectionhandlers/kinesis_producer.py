
from boto import kinesis
import json
from time import sleep
from time import time

class kinesisProducer():

    def __init__(self,region="eu-west-1",stream_names=["BPTK-Demo"]):

        ## Create stream if not already existing
        self.kinesis = kinesis.connect_to_region(region)
        self.stream_names = stream_names

        for stream_name in stream_names:
            if not stream_name in self.kinesis.list_streams()['StreamNames']:
                print("Target Stream does not yet exist. Attempting to create.")
                stream = self.kinesis.create_stream(stream_name, shard_count=8)
                self.kinesis.describe_stream(stream_name)
                sleep(3)

        self.records = []




    def send_data(self, data=None):
        '''
        Send data
        :param data:
        :return:
        '''
        # Send dat


        if data:
            data["timestamp"] = time()
            record = {'Data': json.dumps(data), 'PartitionKey': str(hash(data["id"]))}
            self.records.append(record)


            ## Only send  bunches of 100 records to Kinesis
            if len(self.records) == 100:
                for stream_name in self.stream_names:
                    self.kinesis.put_records(self.records, stream_name)

                self.records = []
                sleep(0.1)