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
                ["New Game", lambda *_: draw_game(["1", "2"], ["K", "B"])],
                        ["Help", lambda *_: open_help()],
                        ["Exit", lambda *_: exit(0)],
                ),
                width=60,
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


def draw_game(open_cards: [], your_cards: [], your_draw: bool = True):
    oc = " - "
    for card in open_cards:
        oc += card + " - "
    yc = " - "
    for card in your_cards:
        yc += card + " - "
    with ptg.WindowManager() as manager:
        window = (
            Window(
                "Du bist am Zug!" if your_draw else "Warten auf deine Gegner...",
                Container(
                    "Aufgedeckte Karten:",
                    Container(oc)
                ),
                Container(
                    "Dein Blatt:",
                    Container(yc)
                ),
                "",
                ["Karte legen", lambda *_: draw(your_cards)] if your_draw else [],
                width=60,
                box="SINGLE",
            )
            .set_title("[210 bold]InGame")
            .center()
        )

        manager.add(window)


def draw(your_cards):
    c = []
    for card in your_cards:
        c.append(["Lege \"" + card + "\"", lambda *_: print(card)])

    with ptg.WindowManager() as manager:
        window = (
            Window(
                "Du bist am Zug!",
                *c,
                width=60,
                box="SINGLE",
            )
            .set_title("[210 bold]InGame")
            .center()
        )

        manager.add(window)


def draw_end(win: bool):
    with ptg.WindowManager() as manager:
        window = (
            Window(
                "",
                Container(
                    "Du hast gewonnen!" if win else "Du hast verloren :(."
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