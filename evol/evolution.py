

class Evolution:

    def __init__(self):
        self.steps = []

    def __iter__(self):
        return self.steps.__iter__()
