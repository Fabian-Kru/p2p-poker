import pytermgui as ptg

from pytermgui import Container, Splitter, Window, InputField
from treys import Card

active_tui = None


def create_tui(node: 'P2PNode'):
    global active_tui
    active_tui = Tui(node)
    return active_tui


def get_tui():
    global active_tui
    return active_tui


class Tui:
    def __init__(self, node: 'P2PNode') -> None:
        CONFIG = """
        config:
            InputField:
                styles:
                    fill: '[@210 bold]{item}'
                    value: '[100 bold]{item}'

            Label:
                styles:
                    value: dim bold

            Window:
                styles:
                    border: '60'
                    corner: '60'

            Container:
                styles:
                    border: '96'
                    corner: '96'
        """

        with ptg.YamlLoader() as loader:
            loader.load(CONFIG)

        self.node = node

    # TODO
    def open_main(self):
        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "Press \"New Game\" to start a new game",
                    "or press \"Help\" to get a brief description of the game.",
                    "",
                    Splitter(
                        ["New Game", lambda *_: self.create_game(False)],
                        ["Find Games", lambda *_: self.find_games()],
                        ["Help", lambda *_: self.open_help()],
                        ["Exit", lambda *_: self.stop(0)],
                    ),
                    width=100,
                    box="DOUBLE",
                )
                .set_title("[210 bold]Main Menu")
                .center()
            )

            manager.add(window)

    def stop(self):
        ptg.WindowManager().stop()
        exit(0)

    def open_help(self):
        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "",
                    Container(
                        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut"
                        "labore et dolore magna aliquyam erat, sed diam voluptua.At vero eos et accusam et justo duo dolores"
                        "et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."
                        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut"
                        "labore et dolore magna aliquyam erat, sed diam voluptua.At vero eos et accusam et justo duo dolores"
                        "et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."
                    ),
                    "",
                    ["Back To Main Menu", lambda *_: self.open_main()],
                    width=60,
                    box="SINGLE",
                )
                .set_title("[210 bold]Help")
                .center()
            )

            manager.add(window)

    def find_games(self):
        game_buttons = []
        for gsm in self.node.get_open_games():
            game_buttons.append([gsm.game.game_id, lambda *_: self.join_game(gsm)])

        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "",
                    Container(
                        "Join one of the following games"
                    ),
                    Container(*game_buttons),
                    "",
                    ["Back To Main Menu", lambda *_: self.open_main()],
                    width=100,
                    box="SINGLE",
                )
                .set_title("[210 bold]Join Game")
                .center()
            )

            manager.add(window)

    def join_game(self, gsm: 'GameSearchMessage'):
        self.node.join_game(gsm)

        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "",
                    Container(
                        "You joined " + gsm.game.game_id,
                        "",
                        "Waiting for start..."
                    ),
                    "",
                    width=100,
                    box="SINGLE",
                )
                .set_title("[210 bold]Waiting")
                .center()
            )

            manager.add(window)

    def create_game(self, renew: bool = True):
        player_list = []
        if renew:
            for player in self.node.game_master.get_current_game().clients:
                player_list.append(player)
        else:
            self.node.create_game()

        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "",
                    Container(
                        "Waiting for players..."
                    ),
                    Container(
                        "[210] Player list:",
                        *player_list
                    ),
                    ["Start Game", lambda *_: self.start_game()],
                    "",
                    ["Back To Main Menu", lambda *_: self.open_main()],
                    width=100,
                    box="SINGLE",
                )
                .set_title("[210 bold]Create Game")
                .center()
            )

            manager.add(window)

    def start_game(self):
        self.node.game_master.start_game(self.node.game_master.get_current_game())

    def get_player(self, name: str):
        return self.node.game_master.get_current_game().poker.players[name]

    def draw_game(self, your_draw: bool = False):
        current_bet = self.node.game_master.get_current_game().poker.current_bet
        available_actions = self.get_player(self.node.game_master.get_current_game().own_name).available_actions(current_bet)

        player_list = []
        for player in self.node.game_master.get_current_game().clients:
            p = self.get_player(player)
            player_list.append(Splitter(p.name, str(p.bet), p.status.name))

        if "board" in self.node.game_master.get_current_game().poker.card_state:
            board = self.node.game_master.get_current_game().poker.card_state["board"]
        else:
            board = []

        with ptg.WindowManager() as manager:
            for w in manager:
                w.close()
                manager.remove(w)

            window = (
                Window(
                    "It's your turn!" if your_draw else "Waiting for opponent...",
                    "",
                    (
                        "Actions:",
                        ["Bet", lambda *_: self.draw_bet()] if "raise" in available_actions else "(Bet not available)",
                        ["Check", lambda *_: self.call_action(
                            self.node.poker_check)] if "check" in available_actions else "(check not available)",
                        ["Fold", lambda *_: self.call_action(
                            self.node.poker_fold)] if "fold" in available_actions else "(fold not available)",
                        ["Call", lambda *_: self.call_action(
                            self.node.poker_call)] if "call" in available_actions else "(call not available)",
                    ) if your_draw else "",
                    "",
                    Splitter(
                        Container(
                            "[210 bold]Player | Bets | Status",
                            *player_list
                        ),
                        Container(
                            Container(
                                "Open Cards:",
                                Container(Card.ints_to_pretty_str(board))
                            ),
                            Container(
                                "Your cards",
                                Container(Card.ints_to_pretty_str(
                                    self.node.game_master.get_current_game().poker.card_state[
                                        self.node.game_master.get_current_game().own_name
                                    ]
                                ))
                            ),
                            "Your Chips: " + str(self.get_player(self.node.game_master.get_current_game().own_name).chips),
                            "Your Bet: " + str(self.get_player(self.node.game_master.get_current_game().own_name).bet),
                            "Everyones Bet: " + str(current_bet)
                        )
                    ),
                    width=128,
                    box="SINGLE",
                )
                .set_title("[210 bold]InGame - " + self.node.game_master.get_current_game().own_name)
                .center()
            )

            manager.add(window)

    def call_action(self, action):
        with ptg.WindowManager() as manager:
            for w in manager:
                w.close()
                manager.remove(w)

            action()

    def draw_bet(self, error: str = ""):
        with ptg.WindowManager() as manager:
            window = (
                Window(
                "[210 bold]" + error,
                    "Your Chips: " + str(self.get_player(self.node.game_master.get_current_game().own_name).chips),
                    "Your Bet: " + str(self.get_player(self.node.game_master.get_current_game().own_name).bet),
                    "",
                    "Add Bet",
                    "",
                    ["5", lambda *_: self._bet(5)],
                    ["10", lambda *_: self._bet(10)],
                    ["50", lambda *_: self._bet(50)],
                    ["100", lambda *_: self._bet(100)],
                    ["500", lambda *_: self._bet(500)],
                    ["1000", lambda *_: self._bet(1000)],
                    "",
                    is_modal=True,
                    width=100,
                    box="SINGLE",
                )
                .set_title("[210 bold]InGame")
                .center()
            )

            window.select(1)
            manager.add(window)

    def _bet(self, val):
        result = (self.get_player(self.node.game_master.get_current_game().own_name)
                  .poker_raise(val,
                               current_bet=self.node.game_master.get_current_game().poker.current_bet)
                  )
        if result < 0:
            self.draw_bet("Invalid input.")

    def draw_end(self, win: bool):
        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "",
                    Container(
                        "You have won! Congratulation!" if win else "You have lost! F. :(."
                    ),
                    "",
                    ["Back To Main Menu", lambda *_: self.open_main()],
                    width=60,
                    box="SINGLE",
                )
                .set_title("[210 bold]End")
                .center()
            )

            manager.add(window)
