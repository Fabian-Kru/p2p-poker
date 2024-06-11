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
                ["New Game", lambda *_: print("new game")],
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
