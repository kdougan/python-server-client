# SERVER

from __future__ import annotations

from threading import Thread
from time import perf_counter, sleep

from phecs import World

from server_client.components import Collider, Ent, Position, Shape, Size, Velocity
from server_client.mod import GameServer
from server_client.systems import (
    collision_system,
    movement_system,
    server_network_system,
)
from server_client.types import State


# ==============================
# SERVER
def main():
    server: GameServer = GameServer()
    server_thread: Thread = Thread(target=server.start)

    world: World = World()
    state: State = State()

    spawn_initial_entities(world)

    server_thread.start()

    tick_rate: int = 30
    time_per_tick: float = 1.0 / tick_rate
    accumulator: float = 0.0

    last_time: float = perf_counter()

    try:
        while not server.running:
            sleep(0.1)
        while server.running:
            current_time: float = perf_counter()
            frame_time: float = current_time - last_time
            last_time = current_time

            accumulator += frame_time

            while accumulator >= time_per_tick:
                server_network_system(world, server, state)
                movement_system(world, state)
                collision_system(world)

                state.dt = time_per_tick
                accumulator -= time_per_tick

            sleep_time: float = time_per_tick - (perf_counter() - current_time)
            if sleep_time > 0:
                sleep(sleep_time)

    except KeyboardInterrupt:
        server.running = False
        server_thread.join()


def spawn_initial_entities(world: World):
    world.spawn(
        Ent(1),
        Position(150.0, 125.0),
        Velocity(-100.0, -100.0),
        Collider(150.0, 125.0, 10.0, 10.0),
        Size(10.0, 10.0),
        Shape("square", "#aaffaa"),
    )

    # 800, 600
    # left wall
    world.spawn(
        Position(0.0, 0.0),
        Collider(0.0, 0.0, 10.0, 600.0),
        Size(10.0, 600.0),
        Shape("square", "#009900"),
    )
    # right wall
    world.spawn(
        Position(790.0, 0.0),
        Collider(790.0, 0.0, 10.0, 600.0),
        Size(10.0, 600.0),
        Shape("square", "#009900"),
    )
    # top wall
    world.spawn(
        Position(0.0, 0.0),
        Collider(0.0, 0.0, 800.0, 10.0),
        Size(800.0, 10.0),
        Shape("square", "#009900"),
    )
    # bottom wall
    world.spawn(
        Position(0.0, 590.0),
        Collider(0.0, 590.0, 800.0, 10.0),
        Size(800.0, 10.0),
        Shape("square", "#009900"),
    )


# ==============================
# START
if __name__ == "__main__":
    main()
