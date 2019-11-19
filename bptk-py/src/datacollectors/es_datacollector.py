#                                                       /`-
# _                                  _   _             /####`-
# | |                                | | (_)           /########`-
# | |_ _ __ __ _ _ __  ___  ___ _ __ | |_ _ ___       /###########`-
# | __| '__/ _` | '_ \/ __|/ _ \ '_ \| __| / __|   ____ -###########/
# | |_| | | (_| | | | \__ \  __/ | | | |_| \__ \  |    | `-#######/
# \__|_|  \__,_|_| |_|___/\___|_| |_|\__|_|___/  |____|    `- # /
#
# Copyright (c) 2018 transentis labs GmbH
# MIT License


#########################
## DATACOLLECTOR CLASS ##
#########################

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from time import sleep
from threading import Thread
import datetime


class ElasticsearchDataCollector:

    def __init__(self, port=9200):
        self.agent_statistics = {}
        self.event_statistics = {}

        self.es = Elasticsearch([{'host': 'es_node1', 'port': port}])

    def record_event(self, time, event):
        """
        Record an event
        :param time: t (int)
        :param event: event instance
        :return: None
        """
        if time not in self.event_statistics:
            self.event_statistics[time] = {}

        if event.name not in self.event_statistics[time]:
            self.event_statistics[time][event.name] = 0

        self.event_statistics[time][event.name] += 1

    def reset(self):
        self.agent_statistics = {}

    def collect_agent_statistics(self, sim_time, agents):
        """
        Collect agent statistics from agent(s)
        :param sim_time: t (int)
        :param agents: list of Agent
        :return: None
        """

        for agent in agents:

            agent_type = agent.agent_type
            agent_id = agent.id

            stats = {}
            stats["id"] = agent.id
            stats["time"] = sim_time
            stats["timestamp"] = datetime.datetime.now() 

            for agent_property_name, agent_property_value in agent.properties.items():
                stats[agent_property_name] = agent_property_value['value']
            #self.statistics_buffer.append(stats)

            #self.es.index(index=str(agent_id) + "_" + str(agent_type).lower(),id=str(agent.id) + "_" + str(sim_time), body=stats)
            self.es.index(index=str(agent_id) + "_" + str(agent_type).lower(), body=stats)

    def statistics(self):
        """
        Get the statistics collected
        :return: Dictionary
        """

        return {}
