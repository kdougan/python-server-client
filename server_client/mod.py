from __future__ import annotations

import socket
import threading
from typing import List


# ==============================
# SERVER
class GameServer:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 65432,
    ) -> None:
        self.host = host
        self.port = port
        self.clients: List[socket.socket] = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.running: bool = False
        self.message_queue: List[bytes] = []
        print(f"Server is listening on {self.host}:{self.port}")

    def broadcast(self, message: bytes, source_client: socket.socket) -> None:
        for client in self.clients:
            if client != source_client:
                try:
                    client.sendall(message)
                except Exception as e:
                    self.clients.remove(client)
                    print("A client was removed due to a failed message send.")
                    print(f"Error: {e}")

    def handle_client(
        self, client_socket: socket.socket, client_address: tuple[str, int]
    ) -> None:
        print(f"Client {client_address} connected.")
        while True:
            try:
                if message := client_socket.recv(1024):
                    self.message_queue.append(message)
                else:
                    break
            except ConnectionResetError:
                print(f"Client {client_address} disconnected unexpectedly.")
                break
            except Exception as e:
                print(f"An error occurred with client {client_address}: {e}")
                break
        client_socket.close()
        self.clients.remove(client_socket)
        print(f"Client {client_address} disconnected.")

    def start(self) -> None:
        print("Server started, waiting for connections...")
        self.running = True
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True,
                )
                thread.start()
            except KeyboardInterrupt as e:
                self.running = False
                for client in self.clients:
                    client.close()
                self.server_socket.close()
                print(f"Server was stopped: {e}")
                break

    def get_messages(self) -> List[bytes]:
        messages = self.message_queue
        self.message_queue = []
        return messages


# ==============================
# CLIENT
class GameClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 65432) -> None:
        self.host = host
        self.port = port
        self.client_socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self.running: bool = False
        self.message_queue: List[bytes] = []

    @property
    def connected(self) -> bool:
        return self.running

    def connect(self) -> None:
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to server")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.running = False

    def start(self) -> None:
        self.connect()
        self.running = True
        thread = threading.Thread(target=self.receive_messages, daemon=True)
        thread.start()

    def receive_messages(self) -> None:
        while self.running:
            try:
                if message := self.client_socket.recv(1024):
                    self.message_queue.append(message)
            except Exception as e:
                print("Lost connection to the server")
                print(f"Error: {e}")
                self.running = False
                break

    def send_message(self, message: bytes) -> None:
        try:
            self.client_socket.sendall(message)
        except Exception as e:
            print("Failed to send message")
            print(f"Error: {e}")
            self.running = False

    def close_connection(self) -> None:
        self.running = False
        self.client_socket.close()

    def get_messages(self) -> List[bytes]:
        messages = self.message_queue
        self.message_queue = []
        return messages
