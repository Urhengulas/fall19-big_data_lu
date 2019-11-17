def build_street(streets):
    streets_return = []

    current_pos = []
    for elem in streets:
        start = elem[0]
        destination = elem[1]
        streets_return += [start]
        current_pos = start



        ## Move right / left
        while not current_pos[0] == destination[0]:

            if destination[0] < current_pos[0]:
                current_pos = (current_pos[0] - 1, current_pos[1])
            else:
                current_pos = (current_pos[0] + 1, current_pos[1])

            streets_return += [current_pos]

        ## Move up / down
        while not current_pos[1] == destination[1]:
            if destination[1] < current_pos[1]:
                current_pos = (current_pos[0], current_pos[1] - 1)
            else:
                current_pos = (current_pos[0], current_pos[1] + 1)

            streets_return += [current_pos]

    return streets_return


def build_random_agents(count,streets,exclude):

    def touches_street(streets,pos):
        def euclidean_distance(pos1, pos2):
            from math import sqrt
            distance = sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
            return int(distance)

        for elem in streets:
            if euclidean_distance(elem,pos) == 1 and pos not in streets:
                return True

        return False

    positions = []
    while len(positions) < count:
        position = []

        import random
        while len(position) == 0 or not touches_street(streets,position) or position in positions or position in exclude:

            position = (random.randint(0,width-1),random.randint(0,height-1))


        positions += [position]

    return positions


height = 20
width = 20

num_chargers = 5



street_markers = [([0,0],[19,17]),

           ( [19,3], [9,19] ) ,
           ([0,9],[19,9])]



streets = build_street(street_markers)
chargers = build_random_agents(3,streets,[])
workshops =  build_random_agents(2,streets,chargers)


transentis_colors = {
    "blue": '#005473',
    "olive": '#9b9b0f',
    "orange": '#ff8200',
    "grey": '#565356',
    "red": '#b4003b',
    "beige": '#ae9b63',
    "turquoise": '#009595',

}



