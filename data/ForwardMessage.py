class ForwardMessage:

    message: str = None
    sender: str = None
    receiver: str = None
    ttl: int = 2

    def __init__(self, sender: str, receiver: str, message: any, ttl: int) -> None:
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.ttl = ttl
        pass

    def __str__(self) -> str:
        return f" sender: {self.sender} receiver: {self.receiver} message: {self.message} ttl: {self.ttl}"
