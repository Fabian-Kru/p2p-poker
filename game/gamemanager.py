class GameMaster:

    def __init__(self):
        self.games = []

    def add_game(self, game):
        print("[game] Game added with id:", game.game_id)
        self.games.append(game)

    def print_game(self):
        print("[game] Games:")
        for game in self.games:
            print(game)

