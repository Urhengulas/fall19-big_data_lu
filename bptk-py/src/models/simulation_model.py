import pickle
from BPTK_Py import Model, Agent
from BPTK_Py.abm.datacollectors import CSVDataCollector
from src.datacollectors import ElasticsearchDataCollector
from src.agents import car, controller
from src.agents.static_agents import destination


class SimulationModel(Model):

    def __init__(self, starttime=0, stoptime=0, dt=1, name="", scheduler=None, data_collector=None):
        """

        :param name: Name as string
        :param scheduler: Implemented instance of scheduler (e.g. simultaneousScheduler)
        :param data_collector: Instance of DataCollector)
        """


        from src.config.conf import chargers, workshops, width, height,streets
        GRID = [[0 for y in range(0, width)] for i in range(0, height)]
        # 1 = CHARGER
        for elem in chargers:
            GRID[elem[0]][elem[1]] = 1

        # 2 = WORKSHOP
        for elem in workshops:
            GRID[elem[0]][elem[1]] = 2

        # 3 = STREET
        for elem in streets:
            GRID[elem[0]][elem[1]] = 3
        self.simple_grid = GRID

        self.time = starttime
        
        # initialize the time pickle
        
        with open("csv/sim_time.pickle",'wb') as my_file_obj:
            pickle.dump(self.time,my_file_obj)   
        
        # the following are needed to track when we last dumped the current simulation time
        
        self.last_write_time = starttime
        self.time_delta=1440

        
        self.static_agents = {}

        super().__init__(starttime, stoptime, dt, name, scheduler, data_collector)

    def create_agent(self, agent_type, agent_properties):
        """
        Create one agent
            :param agent_type: Type of agent
            :return: None
        """

        class NotAnAgentException(Exception):
            pass

        agent = self.agent_factories[agent_type](len(self.agents), self, agent_properties)

        if not isinstance(agent, Agent):
            raise NotAnAgentException(
                "{} is not an instance of BPTK_Py.Agent. Please only use subclasses of Agent".format(agent))

        agent.initialize()
        self.agents.append(agent)
        self.agent_type_map[agent_type].append(agent.id)

    def remove_destination(self, destination):
        try:
            dest = self.static_agents.pop(tuple(destination))

        except: # In case its a charger or workshop..
            pass

    def add_agent(self, pos=(0,0),type=destination,**kwargs):

        if len(kwargs.keys()) > 0:
            agent = type(pos,**kwargs)
        else:
            agent = type(pos)

        self.static_agents[pos] = agent


    def instantiate_model(self):

        self.data_collector = ElasticsearchDataCollector()
        #self.data_collector = CSVDataCollector(prefix="csv/")
        self.register_agent_factory("CONTROLLER",
                                    lambda agent_id, model, properties: controller(agent_id=agent_id, model=model,
                                                                                   properties=properties,
                                                                                   agent_type="CONTROLLER"
                                                                                   ))

        self.register_agent_factory("CAR", lambda agent_id, model, properties: car(agent_id=agent_id, model=model,
                                                                                   properties=properties,
                                                                                   agent_type="CAR"
                                                                                   ))



        self.running = True

    def step(self):
        from src.setup import workshop_objs, charger_objs, street_objs
        scheduler = self.scheduler
        scheduler.run_step(model=self, sim_round=self.time, step=self.dt, progress_widget=None, collect_data=True)
        used_cells = []
        
        # write the current sim time into a pickle

        if(self.time>=self.last_write_time+self.time_delta):
            self.last_write_time+=self.time_delta
            with open("csv/sim_time.pickle",'wb') as time_file_obj:
                pickle.dump(self.time,time_file_obj)   

                
        self.time += 1

