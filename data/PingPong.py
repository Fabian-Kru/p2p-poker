class PingPong:
    name = None
    count = 0

    def __init__(self, name):
        self.name = name
        pass

    def __str__(self):
        return f"name: {self.name} count: {self.count}"
