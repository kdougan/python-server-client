# CLIENT
from __future__ import annotations

import pygame
from phecs.phecs import World

from server_client.mod import GameClient
from server_client.processors import (
    client_network_process,
    input_process,
    render_process,
)
from server_client.types import ClientState


# ==============================
# GAME
class Game:
    def __init__(self) -> None:
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.client: GameClient = GameClient()

        self.world = World()
        self.state = ClientState()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Client")

    def start(self) -> None:
        # Main game loop
        self.client.start()
        while self.client.running:
            client_network_process(state=self.state, client=self.client)
            input_process(client=self.client)
            render_process(screen=self.screen, world=self.world)
            self.state.dt = self.clock.tick(60) * 0.001


# ==============================
# START
if __name__ == "__main__":
    pygame.init()
    Game().start()
