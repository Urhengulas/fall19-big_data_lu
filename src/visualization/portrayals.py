
from src.agents.car import car
from src.agents.static_agents import workshop,charger,destination, pickup,street

from src.config.conf import transentis_colors



def portray(obj):
    if isinstance(obj,car):
        return portrayCar(obj)
    if isinstance(obj,charger):
        return portrayCharger(obj)

    if isinstance(obj,street):
        return portrayStreet(obj)

    if isinstance(obj,workshop):
        return portrayWorkshop(obj)

    if isinstance(obj,destination):
        return portrayDestination(obj)

    if isinstance(obj,pickup):
        return portrayPickup(obj)

def portrayStreet(street):
    assert street is not None
    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "text": "W",
        "Filled": "true",
        "Layer": 0,
        "x": street.position[0],
        "y": street.position[1],
        "Color": "green"
    }

def portrayPickup(pickup):
    assert pickup is not None
    return {
        "Shape": "circle",
        "r": 1,
        "Filled": "false",
        "Layer": 1,
        "text_color" : "white",
        "text": pickup.id,
        "x": pickup.position[0],
        "y": pickup.position[1],
        "Color": "red"}

def portrayDestination(destination):


    assert destination is not None
    return {
        "Shape": "circle",
        "r": 1,
        "text": destination.id,
        "text_color" : "white",
        "Filled": "true",
        "Layer": 1,
        "x": destination.position[0],
        "y": destination.position[1],
        "Color": transentis_colors["turquoise"]}

def portrayCar(car):

    assert car is not None
    states_map = {k : None for k in car.STATES}
    for i,key in enumerate(states_map.keys()):
        states_map[key] = list(transentis_colors.values())[i]
    return {
        "Shape": "rect",
        "text" : car.id,
        "text_color": "white",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 1,
        "x": car.position[0],
        "y": car.position[1],
        "Color": states_map[car.state]
    }

def portrayWorkshop(workshop):

    assert workshop is not None
    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "text": "W",
        "Filled": "true",
        "Layer": 0,
        "x": workshop.position[0],
        "y": workshop.position[1],
        "Color": transentis_colors["beige"]
    }

def portrayCharger(charger):
    assert charger is not None
    return {
        "text": "C",
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 0,
        "x": charger.position[0],
        "y": charger.position[1],
        "Color": "blue"
    }