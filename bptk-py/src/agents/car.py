from BPTK_Py import Agent, Event
from collections import deque
from copy import deepcopy
import random
from src.config.conf import streets


class car(Agent):
    STATES = ["DRIVING", "WAITING", "CHARGING", "FAIL", "REPAIR"]

    def initialize(self):

        self.GRID = self.model.simple_grid

        self.state = "WAITING"


        ## For later analysis. Need to store this
        self.orders = []
        self.selected_order = 1000
        self.order_start = 0
        self.order_finish = 0
        self.result_vectors = {}

        self.step_in_route = 0
        self.route = []
        self.pickup = ()
        self.destination = ()

        self.position =  random.choice(streets)

        self.steps_made = 0
        self.route_lengths = []




    def cost_function(self):

        if self.state == "DRIVING":
            self.cost = self.cost_per_period_driving
        elif self.state == "WAITING":
            self.cost = self.cost_per_period_waiting

        elif self.state == "REPAIR":
            self.cost = self.cost_per_repair

    def revenue_function(self):
        if self.state == "DRIVING" and len(self.pickup) == 0:
            self.revenue = self.price_per_period_driving * (1.0 if self.selected_order[2] < 2000 else 0.9)
            # We give a 10 % discount if waiting time for order confirmation longer than 10

    def find_route(self, start, pickup, destination):
        from collections import deque
        def del_duplicates(lis):
            obs = []
            for i in range(0, len(lis)):
                if i > 0:
                    if not lis[i] == lis[i - 1]:
                        obs += [lis[i]]

                else:
                    obs += [lis[i]]
            return obs

        def compute_route(start, destination):

            def manhattan_distance(pos1, pos2):
                distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

                return distance

            def find_neighbors(pos, nodes):
                # Optimize this! Avoid going through each of the ndoes all the time
                neighbors = []
                for node in nodes:
                    if manhattan_distance(pos, node) == 1:
                        neighbors += [node]

                return neighbors

            def dijkstra(source, dest, nodes):
                inf = float('inf')
                distances = {tuple(vertex): inf for vertex in nodes}

                previous_vertices = {
                    tuple(vertex): None for vertex in nodes
                }
                distances[source] = 0
                vertices = [tuple(x) for x in nodes.copy()]

                while vertices:
                    current_vertex = min(
                        vertices, key=lambda vertex: distances[tuple(vertex)])

                    if distances[tuple(current_vertex)] == inf:
                        break

                    for neighbor in find_neighbors(tuple(current_vertex), nodes):
                        alternative_route = distances[tuple(current_vertex)] + 1
                        if alternative_route < distances[tuple(neighbor)]:
                            distances[tuple(neighbor)] = alternative_route
                            previous_vertices[tuple(neighbor)] = tuple(current_vertex)

                    vertices.remove(tuple(current_vertex))

                path, current_vertex = deque(), dest
                while previous_vertices[tuple(current_vertex)] is not None:
                    path.appendleft(tuple(current_vertex))
                    current_vertex = previous_vertices[tuple(current_vertex)]
                if path:
                    path.appendleft(tuple(current_vertex))
                return path

            from src.config.conf import streets, workshops, chargers

            nodes = streets + workshops + chargers  # All available nodes

            return dijkstra(tuple(start), tuple(destination), nodes)

        ## Way to pickup
        route = compute_route(start, pickup)

        ## Way to destination
        if not pickup == destination:
            route += compute_route(pickup, destination)
        route = del_duplicates(route)

        return route

    def find_nearest_charger(self, chargers, position):
        nearest_charger = chargers[0]
        for elem in chargers:
            if self.manhattan_distance(elem, position) < self.manhattan_distance(position, nearest_charger):
                nearest_charger = elem

        return nearest_charger

    def manhattan_distance(self, pos1, pos2):
        distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        return distance

    def find_best_order(self, order_vectors, nn_model):
        import numpy as np

        best_order = 999
        best_revenue = 0.0
        for i, elem in order_vectors.items():
            expected_revenue = nn_model.predict(np.array([elem]))[0][0]

            if expected_revenue > best_revenue:
                best_order = i
                best_revenue = expected_revenue

        if best_order == 999:
            return None,None

        return best_order, best_revenue

    def act(self, time, round_no, step_no):

        self.cost = 0.0
        self.revenue = 0.0

        self.cost_function()
        self.revenue_function()

        self.total_revenue += self.revenue
        self.total_cost += self.cost

        #######################
        ## WAITING FOR ORDER ##
        #######################
        if self.state == "WAITING":  # Doing nothing as I am just waiting for something to do
            import statistics
            def start_route():
                self.pickup = self.selected_order[0]
                self.destination = self.selected_order[1]

                self.revenue_in_order = 0.0

                from src.agents.static_agents import pickup
                from src.agents.static_agents import destination as destination_type

                self.model.add_agent(pos=self.pickup, type=pickup, id=self.id)
                self.model.add_agent(pos=self.destination, type=destination_type, id=self.id)
                self.state = "DRIVING"

                self.route_lengths += [len(self.route)]

            self.steps_made = 0
            self.step_in_route = 0
            self.route = []



            controller = self.model.agent(0)

            if self.charge < self.charge_threshold * self.capacity:
                from src.config.conf import chargers
                charger = self.find_nearest_charger(chargers=chargers, position=self.position)
                self.selected_order = [charger] + [charger]

                self.route = self.find_route(self.position, self.selected_order[0], self.selected_order[1])
                start_route()
                return

            else:
                if len(controller.orders) == 0:
                    return

                feature_vectors = {}
                for i, order in enumerate(controller.orders):
                    cost_to_start = self.manhattan_distance(order[0], self.position)
                    expected_length = self.manhattan_distance(self.position, order[1])
                    waiting_time = order[2]


                    feature_vectors[i] = (cost_to_start, expected_length, waiting_time)

                self.orders = deepcopy(controller.orders)


                if not controller.trained:
                    self.selected_order = random.choice(self.orders)
                    self.order_start = time

                    self.route = self.find_route(self.position, self.selected_order[0], self.selected_order[1])
                    controller.orders.remove(self.selected_order)

                    index_order = self.orders.index(self.selected_order)

                    self.result_vectors[self.order_start] = list(feature_vectors[index_order]) + [0.0]

                    start_route()

                else:


                    index_order, best_revenue = self.find_best_order(feature_vectors, controller.nn_model)
                    if index_order is None:
                        return

                    self.selected_order = self.orders[index_order]
                    self.order_start = time

                    self.route = self.find_route(self.position, self.selected_order[0], self.selected_order[1])
                    self.result_vectors[self.order_start] = list(feature_vectors[index_order] ) + [best_revenue]

                    controller.orders.remove(self.selected_order)
                    start_route()

            return


        elif self.state == "DRIVING":

            if self.route == []:
                        self.state = "WAITING"
                        return
            
            self.charge -= 1
            self.revenue_in_order += self.revenue

            self.steps_made += 1

            if self.steps_made % 100 == 0 and time > 0:
                self.capacity -= int(self.design_capacity * 0.01)

            if self.capacity < 0.4 * self.design_capacity or self.charge == 0:
                self.state = "FAIL"  # FAILING WHEN LOWER THAN 40 percent of design capacity
                print("[{}] Agent {} failed!".format(time,self.id))
                return

            # MOVE
            try:
                self.position = self.route[self.step_in_route]
                self.pos_x = self.position[0]
                self.pos_y = self.position[1]
            except Exception as e:
                print(self.step_in_route)
                print(self.route)
                print(self.position)
                print(self.destination)
                raise e

            if self.position == self.pickup:
                self.model.remove_destination(self.pickup)
                self.pickup = []

            if self.position == self.destination and self.step_in_route == (
                    len(self.route) - 1):  # Arrived at destination
                self.model.remove_destination(self.destination)
                self.destination = []

                self.state = "WAITING"
                self.route = []

                if self.GRID[self.position[0]][self.position[1]] == 1:
                    self.state = "CHARGING"

                elif self.GRID[self.position[0]][self.position[1]] == 2:
                    self.state = "REPAIR"

                self.step_in_route = 0

                controller_id = self.model.agent_ids("CONTROLLER")[0]  # THERE CAN ONLY BE ONE CONTROLLER

                self.model.agent(controller_id).receive_instantaneous_event(
                    Event(name="finish_route", sender_id=self.id, receiver_id=controller_id, data={}))

                if self.state == "WAITING":
                    import csv

                    self.result_vectors[self.order_start] += [self.revenue_in_order]
                    with open("csv/features.csv".format(self.id), "a") as outfile:
                        wri = csv.writer(outfile, delimiter=";")
                        wri.writerow([time] + self.result_vectors[self.order_start])

                self.revenue_in_order = 0.0

                return
            self.step_in_route += 1
         




        elif self.state == "CHARGING":
            self.step_in_route = 0
            self.charge += 0.1 * self.design_capacity  # Recharge 10 % per round
            if self.charge > self.capacity:
                self.charge = self.capacity

            if self.charge == self.capacity:
                self.state = "WAITING"

        elif self.state == "REPAIR":
            self.step_in_route = 0
            self.capacity = self.design_capacity
            self.state = "WAITING"  # Returning to waiting for customers after one round

        elif self.state == "FAIL":
            self.step_in_route = 0
            pass
        
        self.current_state=self.state
