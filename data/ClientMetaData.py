class ClientMetaData:
    name = None

    def __init__(self, name, port) -> None:
        self.name = name
        self.port = port
        pass

    def __str__(self) -> str:
        return f" name: {self.name} port: {self.port}"

