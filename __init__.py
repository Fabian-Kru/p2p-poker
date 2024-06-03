from server import P2PServer


def main():
    s = P2PServer()
    s.start()
    print('Hello, World!')


main()
