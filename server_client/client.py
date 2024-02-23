# CLIENT
from __future__ import annotations
from time import perf_counter

import pygame
from phecs import World

from server_client.mod import GameClient
from server_client.systems import (
    client_network_sys,
    collision_sys,
    input_sys,
    movement_sys,
    render_sys,
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

        input_sys(client, world, state)

        while accumulator >= time_per_tick:
            client_network_sys(client, world, state)
            movement_sys(world, state)
            collision_sys(world)

            state.dt = time_per_tick
            accumulator -= time_per_tick

        render_sys(screen, world)


# ==============================
# START
if __name__ == "__main__":
    main()
