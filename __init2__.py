import asyncio

from network.network import P2PNode, input_handler
from tui.tui import Tui

server_port = int(input("Enter server_port: "))

if server_port == 1234:
    bootstrap_port = -1
else:
    bootstrap_port = 1234

if server_port == 5454:
    bootstrap_port = -1

network = P2PNode(server_port, bootstrap_port)
#Tui.create_tui(network).open_main()
loop = asyncio.new_event_loop()

loop.run_until_complete(asyncio.gather(
    loop.create_task(network.run()),
    loop.create_task(input_handler(network))
))
