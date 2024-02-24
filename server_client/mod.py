from __future__ import annotations

import socket
import struct
import threading
from dataclasses import dataclass
from typing import Dict, List
from uuid import uuid4

# ==============================
# SERVER


@dataclass
class ServerMessage:
    client_id: str
    data: bytes


class GameServer:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 65432,
    ) -> None:
        self.host = host
        self.port = port
        self.clients: Dict[str, socket.socket] = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.running: bool = False
        self.message_queue: List[ServerMessage] = []
        print(f"Server is listening on {self.host}:{self.port}")

    def broadcast_to_all(self, message: bytes) -> None:
        for _, client in self.clients.items():
            try:
                self.send_message(client, message)
            except Exception as e:
                self.remove_client(client, e)

    def broadcast(self, message: bytes, source_client: socket.socket) -> None:
        for _, client in self.clients.items():
            if client != source_client:
                try:
                    self.send_message(client, message)
                except Exception as e:
                    self.remove_client(client, e)

    def send_message(self, client: socket.socket, message: bytes) -> None:
        try:
            message_length = len(message)
            client.sendall(struct.pack(">I", message_length))
            client.sendall(message)
        except Exception as e:
            self.remove_client(client, e)

    def send_message_to_client(self, client_id: str, message: bytes) -> None:
        if client := self.clients.get(client_id):
            self.send_message(client, message)

    def broadcast_to_all_except(self, client_id: str, message: bytes) -> None:
        if client := self.clients.get(client_id):
            self.broadcast(message, client)

    def remove_client(self, client_id, e=None):
        self.clients.pop(client_id)
        if e:
            print("A client was removed due to a failed message send.")
            print(f"Error: {e}")

    def handle_client(self, client_socket: socket.socket, client_id: str) -> None:
        print(f"Client {client_id} connected.")
        while True:
            try:
                message_length = struct.unpack(">I", client_socket.recv(4))[0]
                message = client_socket.recv(message_length)
                self.message_queue.append(ServerMessage(client_id, message))
            except ConnectionResetError:
                print(f"Client {client_id} disconnected unexpectedly.")
                break
            except Exception as e:
                print(f"An error occurred with client {client_id}: {e}")
                break
        client_socket.close()
        self.clients.pop(client_id)
        print(f"Client {client_id} disconnected.")

    def start(self) -> None:
        print("Server started, waiting for connections...")
        self.running = True
        while self.running:
            try:
                client_socket, _ = self.server_socket.accept()
                client_id = uuid4().hex
                self.clients[client_id] = client_socket
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_id),
                    daemon=True,
                )
                thread.start()
            except KeyboardInterrupt as e:
                self.running = False
                for client in self.clients.values():
                    client.close()
                self.server_socket.close()
                print(f"Server was stopped: {e}")
                break

    def get_messages(self) -> List[ServerMessage]:
        messages = self.message_queue
        self.message_queue = []
        return messages

    def __del__(self) -> None:
        self.running = False
        for client in self.clients.values():
            client.close()
        self.server_socket.close()
        print("Server connection closed")


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
                message_length = struct.unpack(">I", self.client_socket.recv(4))[0]
                message = self.client_socket.recv(message_length)
                self.message_queue.append(message)
            except Exception as e:
                print("Lost connection to the server")
                print(f"Error: {e}")
                self.running = False
                break

    def send_message(self, message: bytes) -> None:
        try:
            message_length = len(message)
            self.client_socket.sendall(struct.pack(">I", message_length))
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

    def __del__(self) -> None:
        self.close_connection()
        print("Client connection closed")
