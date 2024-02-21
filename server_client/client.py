# CLIENT
from __future__ import annotations
from time import perf_counter, sleep

import pygame
from phecs.phecs import World

from server_client.mod import GameClient
from server_client.systems import (
    client_network_system,
    collision_system,
    input_system,
    movement_system,
    render_system,
)
from server_client.types import ClientConnectRequest, State


# ==============================
# GAME
def main():
    client: GameClient = GameClient()

    world = World()
    state = State()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Client")

    tick_rate: int = 60
    time_per_tick: float = 1.0 / tick_rate
    accumulator: float = 0.0

    last_time: float = perf_counter()

    client.start()
    client.send_message(bytes(ClientConnectRequest()))
    while client.running:
        current_time: float = perf_counter()
        frame_time: float = current_time - last_time
        last_time = current_time

        accumulator += frame_time

        input_system(client)

        while accumulator >= time_per_tick:
            client_network_system(client, world)
            movement_system(world, state)
            collision_system(world)

            state.dt = time_per_tick
            accumulator -= time_per_tick

        render_system(screen, world)


# ==============================
# START
if __name__ == "__main__":
    main()
