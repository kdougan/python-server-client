# CLIENT
from __future__ import annotations

import esper
import pygame

from server_client.mod import GameClient
from server_client.processors import (
    ClientNetworkProcessor,
    InputProcessor,
    RenderProcessor,
)


# ==============================
# GAME
class Game:
    def __init__(self) -> None:
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.client: GameClient = GameClient()
        self.dt = 0.0

        esper.add_processor(ClientNetworkProcessor(self.client))
        esper.add_processor(InputProcessor(self.client))
        esper.add_processor(RenderProcessor(640, 480))

    def start(self) -> None:
        # Main game loop
        self.client.start()
        while self.client.running:
            esper.process()
            self.clock.tick(60)


# ==============================
# START
if __name__ == "__main__":
    pygame.init()
    Game().start()
