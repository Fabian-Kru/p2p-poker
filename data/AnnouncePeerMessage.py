class AnnouncePeerMessage:
    known_connections = []
    deliver = False

    def __init__(self, known_connections, deliver) -> None:
        self.known_connections = known_connections
        self.deliver = deliver

    def __str__(self) -> str:
        return f"AnnouncePeerMessage: {self.known_connections} {self.deliver}"
