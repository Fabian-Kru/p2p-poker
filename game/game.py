class Game:

    game_id: str = None

    def __init__(self, game_id) -> None:
        print("[game] Game created with id:", game_id)
        self.game_id = game_id

    def __str__(self) -> str:
        return "Game: " + self.game_id
