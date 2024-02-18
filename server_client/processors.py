from typing import Any

import esper
import pygame
from dinobytes import unpack_msg
from esper import Processor

from server_client.components import Position, Timer, Velocity
from server_client.types import Blackboard, ClientChatMessage, ClientConnect


class MovementProcessor(Processor):
    def process(self):
        for _, (vel, pos) in esper.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y


class TimerProcessor(Processor):
    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard

    def process(self):
        for _, timer in esper.get_component(Timer):
            timer.time += self.blackboard.dt
            if timer.time > timer.interval:
                timer.callback()
                timer.time = 0
                if not timer.repeat:
                    esper.remove_component(_, Timer)


class ServerNetworkProcessor(Processor):
    def __init__(self, server):
        self.server = server
        self.message_counter = 0

    def process(self):
        for msg in self.server.get_messages():
            message = unpack_msg(msg)
            print(f"Server received message: {message}")
            match message:
                case ClientConnect(address):  # type: ignore
                    print(f"Client connected from {address}")
                case ClientChatMessage(message):  # type: ignore
                    print(f"Client sent message: {message}")
                case _:
                    print(f"Unknown message: {message}")


class ClientNetworkProcessor(Processor):
    def __init__(self, client):
        self.client = client
        self.message_counter = 0
        self.connected = False

    def send_message(self, message: Any):
        self.client.send_message(bytes(message))

    def process(self):
        if not self.connected and self.client.connected:
            self.connected = True
            address = self.client.client_socket.getpeername()
            self.send_message(ClientConnect(address))
            return

        for msg in self.client.get_messages():
            message = unpack_msg(msg)
            print(f"Client received message: {message}")


class InputProcessor(Processor):
    def __init__(self, client):
        self.client = client

    def send_message(self, message: Any):
        self.client.send_message(bytes(message))

    def process(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif event.key == pygame.K_SPACE:
                    print("Space pressed")
                    self.send_message(ClientChatMessage("space pressed"))


class RenderProcessor(Processor):
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Game Client")

    def process(self):
        self.screen.fill((0, 0, 0))
        for _, (pos, _) in esper.get_components(Position, Velocity):
            pygame.draw.circle(self.screen, (255, 255, 255), (pos.x, pos.y), 4)
        pygame.display.flip()
