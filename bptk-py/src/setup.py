from .config.conf import chargers,workshops, width, height,streets
from src.agents.static_agents import workshop,charger,street
from src.agents.car import car
import BPTK_Py
import random


from src.config.conf import transentis_colors

charger_objs = [charger(chargers[i]) for i in range(0,len(chargers))]

workshop_objs = [workshop(workshops[i]) for i in range(0,len(workshops))]

street_objs = [street(streets[i]) for i in range(0,len(streets))]



def setup_model(bptk):
    model = bptk.scenario_manager_factory.scenario_managers["CARMODEL"].scenarios["scenario"].model
    return model


