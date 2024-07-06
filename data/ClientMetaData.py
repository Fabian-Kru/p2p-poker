class ClientMetaData:
    name = None
    port = None

    def __init__(self, name: str, port: int) -> None:
        self.name = name
        self.port = port
        pass

    def __str__(self) -> str:
        return f" name: {self.name} port: {self.port}"

