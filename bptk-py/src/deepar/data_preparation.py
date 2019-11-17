import BPTK_Py
import pandas as pd
import json

def run_car_ABM(scenario_manager="CARMODEL"):

    bptk = BPTK_Py.instantiate(loglevel="WARN")

    bptk.run_simulations(
        scenario_managers=[scenario_manager],
        scenarios=["scenario"],
        agents=["agent"],
        progressBar=True
    )


def create_dataset(filename,freq,start_date,target_value,agent_count):
    df = pd.read_csv(filename, sep=";")
    df.index = pd.date_range(start_date, periods=len(df), freq=freq)

    global_dataset = []

    def create_agent_dataset(df,target_value):
        temp_dic = {}
        for elem in df.iterrows():
            index = df.index[0].strftime('%Y-%m-%d')

            if index not in temp_dic.keys():
                temp_dic[index] = {"start": index, "target": []}

            target = elem[1][target_value]
            temp_dic[index]["target"] += [target.copy()]

        dataset = [value for key, value in temp_dic.items()]
        return dataset


    for id in range(0,agent_count):
        global_dataset += create_agent_dataset(df.loc[df['id']==id],target_value)

    return global_dataset



def create_trainSet(data,horizon):
    trainSet = []


    for elem in data:
        if horizon > 0:
            temp_dic = {"start": elem["start"] + " 00:00:00", "target": elem["target"][0:-horizon]}
        else:
            temp_dic = {"start": elem["start"] + " 00:00:00", "target": elem["target"]}
        trainSet += [temp_dic]
    return trainSet

def create_testSet(data):
    return create_trainSet(data,0)


def write_dataset(filename, data):
    outfile = open(filename, "w")
    for elem in data:
        outfile.write(json.dumps(elem) + '\n')

    outfile.close()