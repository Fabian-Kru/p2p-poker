import sys
import threading

from network.network import P2PNode
from tui.tui import Tui

server_port = int(input("Enter server_port: "))

if server_port == 1234:
    bootstrap_port = -1
else:
    bootstrap_port = 1234

if server_port == 5454:
    bootstrap_port = -1

network = P2PNode(server_port, bootstrap_port)

#tui = Tui.create_tui(network)

try:
    input_thread = threading.Thread(target=network.process_input)
    #tui_thread = threading.Thread(target=tui.open_main)
    server_thread = threading.Thread(target=network.run)

    input_thread.daemon = True
    #tui_thread.daemon = True
    server_thread.daemon = True

    #tui_thread.start()
    input_thread.start()
    server_thread.start()
except Exception as e:
    print("Error starting threads", e)
    sys.exit(1)

try:
    while True:
        pass
except (SystemExit, KeyboardInterrupt):
    for client in network.clients:
        client.close_connection()
    print("Shutting down...")
    sys.exit(0)
