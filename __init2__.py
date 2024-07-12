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

#Tui.create_tui(network).open_main()

input_thread = threading.Thread(target=network.process_input)
server_thread = threading.Thread(target=network.run)

input_thread.daemon = True
server_thread.daemon = True

input_thread.start()
server_thread.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Shutting down...")
    sys.exit(0)
