import sys

from server_client.server import main as server
from server_client.client import main as client

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        server()
    else:
        client()
