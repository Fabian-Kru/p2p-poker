import pytermgui as ptg
from pytermgui import Container, Label, Splitter, Button, Checkbox, Window


def open_main():
    with ptg.WindowManager() as manager:
        window = (
            Window(
                "Press \"New Game\" to start a new game",
                "or press \"Help\" to get a brief description of the game.",
                "",
                Splitter(
                ["New Game", lambda *_: create_game(["blabla", "test"])], # ToDo Funktion zum Starten hinzufügen
                        ["Find Games", lambda *_: find_games()],
                        ["Help", lambda *_: open_help()],
                        ["Exit", lambda *_: exit(0)],
                ),
                width=100,
                box="DOUBLE",
            )
            .set_title("[210 bold]Main Menu")
            .center()
        )

        manager.add(window)


def open_help():
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
                ["Back To Main Menu", lambda *_: open_main()],
                width=60,
                box="SINGLE",
            )
            .set_title("[210 bold]Help")
            .center()
        )

        manager.add(window)


def find_games():
    # ToDo: Add Method to get all open games
    games = ["A", "B", "C", "Kekse"]
    game_buttons = []
    for game in games:
        game_buttons.append([game, lambda *_: print("Start " + game)]) # ToDo: Instead of print add the join function

    with ptg.WindowManager() as manager:
        window = (
            Window(
                "",
                Container(
                    "Join one of the following games"
                ),
                Container(*game_buttons),
                "",
                ["Back To Main Menu", lambda *_: open_main()],
                width=100,
                box="SINGLE",
            )
            .set_title("[210 bold]Join Game")
            .center()
        )

        manager.add(window)


def create_game(players):
    # Aufrufen, sobald Spiel erstellt wurde...
    player_list = []
    for player in players:
        player_list.append(player)

    with ptg.WindowManager() as manager:
        window = (
            Window(
                "",
                Container(
                    "Waiting for players..."
                ),
                Container(
                    "Player list:",
                    *player_list
                ),
                "",
                ["Back To Main Menu", lambda *_: open_main()],
                width=100,
                box="SINGLE",
            )
            .set_title("[210 bold]Create Game")
            .center()
        )

        manager.add(window)


def draw_game(open_cards: [], your_cards: [], chips: int = 0, your_draw: bool = True,
              raise_chips: bool = True, check: bool = True, fold: bool = True, call: bool = True):
    oc = " - "
    for card in open_cards:
        oc += card + " - "
    yc = " - "
    for card in your_cards:
        yc += card + " - "

    with ptg.WindowManager() as manager:
        window = (
            Window(
                "It's your turn!" if your_draw else "Waiting for opponent...",
                Container(
                    "Open Cards:",
                    Container(oc)
                ),
                Container(
                    "Your cards",
                    Container(yc)
                ),
                "Your Chips: " + str(chips),
                "",
                Container(
                    "Actions:",
                    ["Bet", lambda *_: bet(your_cards)] if raise_chips else "(Bet not available)",
                    ["Check", lambda *_: print("Todo")] if check else "(check not available)",
                    ["Fold", lambda *_: print("Todo")] if fold else "(fold not available)",
                    ["Call", lambda *_: print("Todo")] if call else "(call not available)",
                ) if your_draw else "",
                width=60,
                box="SINGLE",
            )
            .set_title("[210 bold]InGame")
            .center()
        )

        manager.add(window)


def bet(your_credits: int = 0):
    pass


def draw_end(win: bool):
    with ptg.WindowManager() as manager:
        window = (
            Window(
                "",
                Container(
                    "You have won! Congratulation!" if win else "You have lost! F. :(."
                ),
                "",
                ["Back To Main Menu", lambda *_: open_main()],
                width=60,
                box="SINGLE",
            )
            .set_title("[210 bold]End")
            .center()
        )

        manager.add(window)
