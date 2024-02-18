# SERVER

from __future__ import annotations
from time import perf_counter, sleep
from server_client.components import Timer
from server_client.types import Blackboard
from server_client.mod import GameServer
from threading import Thread
import esper
from server_client.processors import (
    MovementProcessor,
    TimerProcessor,
    ServerNetworkProcessor,
)

# ==============================
# SERVER


class Game:
    def __init__(self) -> None:
        self.tick_rate = 30
        self.clock = perf_counter()
        self.server: GameServer = GameServer()
        self.server_thread = Thread(target=self.server.start, daemon=True)
        self.blackboard = Blackboard()

        esper.add_processor(MovementProcessor())
        esper.add_processor(TimerProcessor(self.blackboard))
        esper.add_processor(ServerNetworkProcessor(self.server))

        esper.create_entity(Timer(5, True, lambda: print(".")))

    def start(self) -> None:
        # Main game loop
        self.server_thread.start()

        while not self.server.running:
            sleep(0.1)

        try:
            while self.server.running:
                esper.process()
                self.dt = self.tick(self.tick_rate)
        except KeyboardInterrupt:
            self.server.running = False
            self.server_thread.join()

    def tick(self, tick_rate: int) -> float:
        # Limit tick rate to self.tick_rate per second and return elapsed time
        elapsed = perf_counter() - self.clock
        sleep_time = 1 / tick_rate - elapsed
        if sleep_time > 0:
            sleep(sleep_time)
        elapsed = perf_counter() - self.clock
        self.clock = perf_counter()
        return elapsed


# ==============================
# START

if __name__ == "__main__":
    Game().start()
