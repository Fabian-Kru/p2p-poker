import asyncio
import pickle
from typing import TYPE_CHECKING, List

from network.client import P2PClient
from data.Message import Message
from data.game.GameSearchMessage import GameSearchMessage
from game.game import Game
from game.gamemanager import GameMaster
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
        asyncio.ensure_future(c.connect_to_socket())
        return True

    def get_client_by_name(self, name: str) -> [P2PClient, None]:
        for c in self.clients:
            if c.knows_client(name):
                return c
        return None

    def knows_client(self, receiver: str) -> bool:
        return self.server.known_client(receiver) or (True in [x.knows_client(receiver) for x in self.clients])

    async def send_to_client(self, client_name: str, message: bytes) -> None:
        # check if client knows client
        client = self.get_client_by_name(client_name)

        if client is not None:
            asyncio.ensure_future(client.send_message(message))
            return

        if self.server.known_client(client_name):
            if not isinstance(message, (bytes, bytearray)):
                message = pickle.dumps(message)
            asyncio.ensure_future(self.server.send_to_client(client_name, message))
            return

    async def broadcast_message_with_ttl(self, message: str, ttl: int) -> None:
        for i, client in enumerate(self.clients):
            if i < ttl:
                asyncio.ensure_future(client.send_message(message))

    async def broadcast_message(self, message: str) -> None:
        for c in self.clients:
            asyncio.ensure_future(c.send_message(message))

    async def run(self) -> None:
        if self.bootstrap_port == -1:
            await self.server.start(self, -1)
            return
        await asyncio.create_task(self.server.start(self, self.bp)),

    async def process_input(self, command: str) -> None:

        if command == "create_game":
            game = self.game_master.create_game("Game-" + str(self.sp))
            await self.server.broadcast_message(GameSearchMessage(ttl=2, sender=self.name, game=game.get_client_object()))
            return

        if command == "start_game":
            print("[server] Starting game")
            game = self.game_master.get_or_add_game(Game("Game-" + str(self.sp), self.name, self.name, None))
            if game is None:
                print("[server] Game not found")
                return
            self.game_master.start_game(game)
            return

        if command == "cards":
            print("[server] Requesting cards")
            for player in self.game_master.get_current_game().poker.players:
                self.game_master.get_current_game().poker.request_card_codes(player)
                break
            return

        if command == "raise":
            print("client-" + str(self.sp))
            result = (self.game_master
                      .get_current_game()
                      .poker
                      .player_action(self.game_master, self.game_master.get_current_game(), "client-" + str(self.sp), "raise", 10))
            log("[server] Raise result:", result)
            return

        if command == "check":
            result = (self.game_master
                      .get_current_game()
                      .poker
                      .player_action(self.game_master, self.game_master.get_current_game(), "client-" + str(self.sp),
                                     "check", 0))
            log("[server] Check result:", result)
            return

        if command == "fold":
            result = (self.game_master
                      .get_current_game()
                      .poker
                      .player_action(self.game_master, self.game_master.get_current_game(), self.name, "fold", 10))
            log("[server] Fold result:", result)
            return

        if command == "call":
            result = (self.game_master
                      .get_current_game()
                      .poker
                      .player_action(self.game_master, self.game_master.get_current_game(), self.name, "call", 10))
            log("[server] Call result:", result)
            return

        if command == "blinds":
            result = (self.game_master
                      .get_current_game()
                      .poker
                      .player_action(self.game_master, self.game_master.get_current_game(), self.name, "blinds", 10))
            log("[server] Blinds result:", result)
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
            await self.send_to_client(client_name, pickle.dumps(Message(message)))
            return


async def input_handler(_network) -> None:
    while True:
        command = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        await _network.process_input(command)
