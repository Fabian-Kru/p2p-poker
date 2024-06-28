class Game:

    def __init__(self, game_id):
        print("[game] Game created with id:", game_id)
        self.game_id = game_id

    def __str__(self):
        return "Game: " + self.game_id
