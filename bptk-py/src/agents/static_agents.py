class workshop():

    def __init__(self,position):
        self.position = position

class charger():
    def __init__(self, position):
        self.position = position

class destination():
    def __init__(self,position,**kwargs):
        self.position = position
        self.id = kwargs["id"]

class pickup():
    def __init__(self,position,**kwargs):
        self.position = position
        self.id = kwargs["id"]


class street():
    def __init__(self,position,**kwargs):
        self.position = position