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


    # Make a world that is 50x50, on a 250x250 display.
    #canvas_element = CanvasGrid(portray, height, width,500,500)

   # colors = list(transentis_colors.values())

    #series_controller = [{"Label": id,"Color":random.choice(colors)} for id in model.agent_ids("CONTROLLER")]
    #series = [{"Label": id,"Color":random.choice(colors)} for id in model.agent_ids("CAR")]
    #charge_chart = CarChartModule(series=series)
    #controller_chart = ControllerChartModule(series=series_controller)
    #revenue_cost_chart = CarCostChartModule(series=[{"Label": "revenue","Color":transentis_colors["orange"]},{"Label":"cost","Color": transentis_colors["blue"]}])
    #total_revenue_cost_chart = CarCostChartModule(
      #  series=[{"Label": "total_revenue", "Color": transentis_colors["orange"]}, {"Label": "total_cost", "Color": transentis_colors["blue"]}])


    used_cells = []

    #for agent in model.agents:
     #   if isinstance(agent, car):
     #       used_cells += [agent.position]
     #       model.grid.place_agent(agent, (agent.position[0], agent.position[1]))

    #for agent in workshop_objs:
    #    used_cells += [agent.position]
    #    model.grid.place_agent(agent, (agent.position[0], agent.position[1]))

    #for agent in charger_objs:
    #    used_cells += [agent.position]
    #    model.grid.place_agent(agent, (agent.position[0], agent.position[1]))

    #for agent in street_objs:
    #    if not agent.position in used_cells:
    #        model.grid.place_agent(agent, agent.position)

    return model


