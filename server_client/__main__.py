import sys

from server_client.server import Game as ServerGame
from server_client.client import Game as ClientGame

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        ServerGame().start()
    else:
        ClientGame().start()
