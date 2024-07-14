import pickle
from typing import TYPE_CHECKING, List

from data.Message import Message
from data.game.GameJoinMessage import GameJoinMessage
from data.game.GameSearchMessage import GameSearchMessage
from game.game import Game
from game.gamemanager import GameMaster
from network.client import P2PClient
from util.logging import log

if not TYPE_CHECKING:
    from network.server import P2PServer


class P2PNode:

    def __init__(self, _server_port: int, port: int) -> None:
        self.bootstrap_port = port
        self.server = P2PServer(_server_port, self)
        self.clients: List[P2PClient] = []
        self.open_games = []
        self.bp = port
        self.sp = _server_port
        self.name = "client-" + str(self.sp)
        GameMaster.create_master(self)
        self.game_master = GameMaster.get_master()  # shared between client and server to avoid sync problems

    def add_game_search(self, game_search) -> None:
        log("[client] Added new game_search", game_search.game)
        self.open_games.append(game_search)

    def get_open_games(self) -> List[GameSearchMessage]:
        return self.open_games

    def has_connection(self, client_name: [str, None], port: int) -> bool:
        for c in self.clients:
            if c.uid == client_name or c.port == port:
                return True
        return False

    def connect_to_node(self, ip: str, port: int) -> bool:
        self.name = "client-" + str(self.sp)
        if self.has_connection(None, port):
            return False
        c = P2PClient(self, port, "client-" + str(self.sp))
        self.clients.append(c)
        c.connect_to_socket()
        return True

    def get_client_by_name(self, name: str) -> [P2PClient, None]:
        for c in self.clients:
            if c.knows_client(name):
                return c
        return None

    def knows_client(self, receiver: str) -> bool:
        return self.server.known_client(receiver) or (True in [x.knows_client(receiver) for x in self.clients])

    def send_to_client(self, client_name: str, message: any) -> None:
        # check if client knows client
        client = self.get_client_by_name(client_name)

        if not isinstance(message, (bytes, bytearray)):
            message = pickle.dumps(message, protocol=None)

        if client is not None:
            client.send_message(message)
            return

        if self.server.known_client(client_name):
            self.server.send_to_client(client_name, message)
            return

    def broadcast_message_with_ttl(self, message: str, ttl: int) -> None:
        for i, client in enumerate(self.clients):
            if i < ttl:
                client.send_message(message)

    def broadcast_message(self, message: str) -> None:
        for c in self.clients:
            c.send_message(message)

    def run(self) -> None:
        if self.bootstrap_port == -1:
            self.server.start(self, -1)
            return
        self.server.start(self, self.bp)

    def process_input(self) -> None:
        while True:
            command = input(">")
            print("[server] Received command:", command)
            self.__process_input(command)

    def join_any_game(self) -> None:
        if not self.get_open_games():
            print("[server] No open games")
            return
        game_search = self.open_games.pop(0)
        self.join_game(game_search)

    def join_game(self, game_search: GameSearchMessage) -> None:
        if game_search is None:
            print("[server] game_search is None")
            return
        game = game_search.game
        self.game_master.add_game(game)
        game = self.game_master.get_or_add_game(game)
        game.add_client_local(self.name)
        self.send_to_client(game_search.sender, GameJoinMessage(game, self.name))
        log("[client] >GameJoinMessage sent", game, self.name)

    def start_game(self) -> None:
        print("[server] Starting game")
        game = self.game_master.get_or_add_game(Game("Game-" + str(self.sp), self.name, self.name, None))
        if game is None:
            print("[server] Game not found")
            return
        self.game_master.start_game(game)

    def create_game(self) -> None:
        game = self.game_master.create_game("Game-" + str(self.sp))
        self.server.broadcast_message(GameSearchMessage(ttl=2, sender=self.name, game=game.get_client_object()))

    def poker_raise(self, chips: int) -> None:
        result = (self.game_master
                  .get_current_game()
                  .poker
                  .player_action(self.game_master, self.game_master.get_current_game(), "client-" + str(self.sp),
                                 "raise", chips))
        log("[server] Raise result:", result)

    def poker_check(self) -> None:
        result = (self.game_master
                  .get_current_game()
                  .poker
                  .player_action(self.game_master, self.game_master.get_current_game(), "client-" + str(self.sp),
                                 "check", 1))
        log("[server] Check result:", result)

    def poker_fold(self) -> None:
        result = (self.game_master
                  .get_current_game()
                  .poker
                  .player_action(self.game_master, self.game_master.get_current_game(), "client-" + str(self.sp),
                                 "fold", 10))
        log("[server] Fold result:", result)

    def poker_call(self) -> None:
        result = (self.game_master
                  .get_current_game()
                  .poker
                  .player_action(self.game_master, self.game_master.get_current_game(), self.name, "call", 10))
        log("[server] Call result:", result)

    def poker_blind(self, chips: int) -> None:
        result = (self.game_master
                  .get_current_game()
                  .poker
                  .player_action(self.game_master, self.game_master.get_current_game(), self.name, "blinds", chips))
        log("[server] Blinds result:", result)

    def new_round(self):
        self.game_master.new_dealer_and_round(self.game_master.get_current_game())

    def shutdown(self) -> None:
        for client in self.clients:
            client.close_connection()
        self.server.close_connections()

    def __process_input(self, command: str) -> None:

        if command == "stop":
            self.shutdown()
            return

        if command == "create_game":
            self.create_game()
            return

        if command == "new_round":
            self.new_round()
            return

        if command == "join":
            self.join_any_game()
            return

        if command == "start_game":
            self.start_game()
            return

        if command == "cards":
            print("[server] Requesting cards")
            for player in self.game_master.get_current_game().poker.players:
                self.game_master.get_current_game().poker.request_card_codes(player)
                break
            return

        if command == "raise":
            self.poker_raise(int(input("Enter raise amount: ")))
            return

        if command == "check":
            self.poker_check()
            return

        if command == "fold":
            self.poker_fold()
            return

        if command == "call":
            self.poker_call()
            return

        if command == "blinds":
            self.poker_blind(int(input("Enter blind amount: ")))
            return

        if command == "list":
            log("[server] own-name:", "client-" + str(self.sp))
            log("[server] clients:", [c.uid for c in self.clients])
            log("[client] clients", [v.name for k, v in self.server.clients.items()])
            return

        if command == "games":
            self.game_master.print_game()
            return

        if command == "poker" or command == "p":
            log(self.game_master.get_current_game().poker)
            return

        if command.startswith("send"):
            parts = command.split(" ")
            if len(parts) < 3:
                log("Invalid command")
                return
            client_name = parts[1]
            message = " ".join(parts[2:])
            self.send_to_client(client_name, pickle.dumps(Message(message), protocol=None))
            return
        print("Unknown command")
