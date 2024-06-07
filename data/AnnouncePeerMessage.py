class AnnouncePeerMessage:
    known_connections = []
    deliver = False

    def __init__(self, known_connections, deliver):
        self.known_connections = known_connections
        self.deliver = deliver

    def __str__(self):
        return f"AnnouncePeerMessage: {self.known_connections} {self.deliver}"
