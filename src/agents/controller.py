from BPTK_Py import Agent, Event
import copy
import random, math
from src.config.conf import chargers


def euclidean_distance(pos1, pos2):
    from math import sqrt
    distance = sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
    return int(distance)


class controller(Agent):
    STATES = ["RUNNING"]

    def initialize(self):
        self.agent_type = "CONTROLLER"
        self.state = "RUNNING"

        self.finished_this_round = 0

        self.route_lengths = (0, 0, 0)
        self.trained = False




        self.orders = []

        self.GRID = self.model.simple_grid

        self.register_event_handler(states=["RUNNING"], event="finish_route", handler=self.handle_finish_route)

        from keras.models import Sequential
        from keras.layers.core import Dense
        from keras.optimizers import Adam
        learning_rate = 0.001
        self.nn_model = Sequential()
        self.nn_model.add(Dense(24, input_dim=3, activation='relu'))
        self.nn_model.add(Dense(24, activation='relu'))
        self.nn_model.add(Dense(1, activation='linear'))
        self.nn_model.compile(loss='mse', optimizer=Adam(lr=learning_rate))

        import os
        if os.path.isfile("csv/features.csv"):
             self.__train_model()

    def __train_model(self):
        #print("STARTING TRAINING OF NEURAL NETWORK. ")
        self.trained = False
        import pandas as pd
        df = pd.read_csv("csv/features.csv", sep=";",
                         names=["time","distance_to_pickup", "route_length","waiting_time","exp_rev", "Revenue"], index_col=None)
        df.pop("exp_rev")
        df.pop("time")
        from sklearn.model_selection import train_test_split
        data = df[[col for col in df.columns if col != "Revenue"]]
        y = df[[col for col in df.columns if col == "Revenue"]]
        X_train, X_test, y_train, y_test = train_test_split(data, y)

        self.nn_model.fit(x=data, y=y, epochs=1000, verbose=0)

        #print("Test Error: " + str(self.nn_model.evaluate(X_test,y_test,verbose=0)))

        self.trained = True
        model_json = self.nn_model.to_json()
        with open("./models/neural_network.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.nn_model.save_weights("./models/neural_network_weights.h5")


        pass

    def handle_finish_route(self, event):

        self.finished_this_round += 1

    def act(self, time, round_no, step_no):

        if time % 1000 == 0 and time > 0:

            self.__train_model()


        def create_order():
            from src.config.conf import streets
            def manhattan_distance(pos1, pos2):
                distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

                return distance

            import random

            pickup = (0,0)

            while pickup == (0,0) or pickup not in streets:
                pickup = (
                    random.randint(0, len(self.GRID[0])),
                                   random.randint(0, len(self.GRID))
                                   )


            destination = pickup

            while destination == pickup or destination not in streets or manhattan_distance(destination,pickup) < 5:
                destination = (
                    random.randint(0, len(self.GRID[0])),
                    random.randint(0, len(self.GRID))
                )


            return [pickup, destination,0]

        sum_waiting_time = 0
        for order in self.orders:
            order[2] += 1
            sum_waiting_time += order[2]

        self.customer_average_waiting_time = 0 if len(self.orders) == 0 else sum_waiting_time / len(self.orders)




        rnd = random.uniform(0,1)
        if rnd < 0.2:
            #if len(self.orders) < len(self.model.agent_ids("CAR")):
            no_orders = math.ceil(rnd) * self.max_orders_per_round

            for _ in range(0,no_orders):
                self.orders += [create_order()]



