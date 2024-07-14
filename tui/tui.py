import pytermgui as ptg

from pytermgui import Container, Splitter, Window, InputField
from treys import Card

import data.game


class Tui:
    active_tui = None

    @staticmethod
    def create_tui(node: 'P2PNode'):
        global active_tui
        active_tui = Tui(node)
        return active_tui

    @staticmethod
    def get_tui():
        global active_tui
        return active_tui

    def __init__(self, node: 'P2PNode') -> None:
        CONFIG = """
        config:
            InputField:
                styles:
                    fill: '[@236]{item}'
                    value: '[72]{item}'

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
                        ["Exit", lambda *_: exit(0)],
                    ),
                    width=100,
                    box="DOUBLE",
                )
                .set_title("[210 bold]Main Menu")
                .center()
            )

            manager.add(window)

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
            for player in self.node.game_master.get_current_game().clients():
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
        # ToDo draw game!

    # TODO
    def draw_game(self, your_draw: bool = True,
                  raise_chips: bool = True, check: bool = True, fold: bool = True, call: bool = True):
        player_list = []
        for player in self.node.game_master.get_current_game().clients():
            player_list.append(Splitter(player.name, str(player.bet), player.status.name))

        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "It's your turn!" if your_draw else "Waiting for opponent...",
                    Splitter(
                        Container(
                            "[210 bold]Player | Bets | Status",
                            *player_list
                        ),
                        Container(
                            Container(
                                "Open Cards:",
                                Container(Card.ints_to_pretty_str(self.node.game_master.get_current_game().cards))
                            ),
                            Container(
                                "Your cards",
                                Container(self.node.game_master.get_current_game().poker.card_state[
                                              self.node.game_master.get_current_game().myself.name])
                            ),
                            "Your Chips: " + str(self.node.game_master.get_current_game().myself.chips),
                            "Your Bet: " + str(self.node.game_master.get_current_game().myself.bet),
                            "Everyones Bet: " + str(self.node.game_master.get_current_game().poker.current_bet)
                        )
                    ),
                    "",
                    Container(
                        "Actions:",
                        ["Bet", lambda *_: self.draw_bet()] if raise_chips else "(Bet not available)",
                        ["Check", lambda *_: self.node.poker_check()] if check else "(check not available)",
                        ["Fold", lambda *_: self.node.poker_fold()] if fold else "(fold not available)",
                        ["Call", lambda *_: self.node.poker_call()] if call else "(call not available)",
                    ) if your_draw else "",
                    width=128,
                    box="SINGLE",
                )
                .set_title("[210 bold]InGame")
                .center()
            )

            manager.add(window)

    def draw_bet(self, error: str = ""):
        field = InputField()
        field.bind(ptg.keys.RETURN, lambda f, _: self._bet(f.value))

        with ptg.WindowManager() as manager:
            window = (
                Window(
                    "[210 bold]" + error,
                    "",
                    Container(
                        "Your Chips: " + str(self.node.game_master.get_current_game().myself.chips),
                        "Your Bet: " + str(self.node.game_master.get_current_game().myself.bet),
                        "",
                        Splitter(
                            "Add Bet",
                            field
                        )
                    ),
                    "",
                    width=60,
                    box="SINGLE",
                )
                .set_title("[210 bold]InGame")
                .center()
            )

            manager.add(window)

    def _bet(self, val):
        if type(val) is not int or val < 1:
            self.draw_bet("Invalid input.")
            return

        result = (self.node.game_master
                  .get_current_game().myself.poker_raise(1, current_bet=0, game_master=self.game_master))
        if result < 0:
            self.draw_bet("Invalid input.")

        # ToDo
        self.draw_game(["open1, open2"], ["yours1", "yours2"], 100, 10, 1000)

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
