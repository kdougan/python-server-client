# SERVER

from __future__ import annotations

from threading import Thread
from time import perf_counter, sleep

from phecs import World

from server_client.components import Ent, Message, Position, Velocity
from server_client.mod import GameServer
from server_client.processors import (
    movement_process,
    server_network_process,
)
from server_client.types import ServerState

# ==============================
# SERVER


class Game:
    def __init__(self) -> None:
        self.tick_rate = 30
        self.clock = perf_counter()
        self.server: GameServer = GameServer()
        self.server_thread = Thread(target=self.server.start, daemon=True)

        self.world = World()
        self.state = ServerState()

    def start(self) -> None:
        self.server_thread.start()

        while not self.server.running:
            sleep(0.1)

        self.world.spawn(
            Ent(1),
            Position(0.0, 0.0),
            Velocity(0.1, 0.1),
            Message(
                """Excepteur amet elit sint mollit deserunt commodo incididunt. Do minim laborum sint non veniam dolore exercitation. Anim in sit exercitation velit nostrud amet aliqua minim nulla cillum sunt velit adipisicing qui. Voluptate nulla eu do adipisicing duis ut fugiat commodo esse incididunt exercitation ipsum cillum. Irure amet quis qui duis pariatur deserunt ipsum id consectetur. Id consectetur irure culpa laboris do id nulla mollit do fugiat reprehenderit ut dolore.

Eu esse sunt veniam excepteur veniam ad nulla. Velit laboris ullamco Lorem proident irure irure Lorem. Minim elit proident laboris ipsum quis. Ipsum laboris sint aliqua duis dolor dolore enim sit nostrud consectetur reprehenderit exercitation. Voluptate ut sint et sint dolor ea culpa exercitation non est non. Labore mollit ad tempor labore deserunt voluptate eu tempor.

Id aliquip ex Lorem laboris fugiat occaecat. Lorem officia culpa Lorem commodo. Quis incididunt consectetur aliquip reprehenderit nulla proident enim duis occaecat elit. Officia occaecat deserunt incididunt Lorem adipisicing magna esse eu cupidatat commodo adipisicing nostrud. Anim Lorem sunt enim ex duis elit sunt proident id irure minim sint occaecat. Amet occaecat laboris irure aute minim do in culpa proident excepteur esse voluptate elit. Ea do velit ex mollit est aliqua nulla.

Minim veniam esse ea deserunt irure. Amet deserunt officia consequat ad anim laboris ut. Eiusmod aliqua elit officia aliquip esse pariatur adipisicing laborum voluptate nulla nisi pariatur id esse. Et incididunt ea pariatur do ipsum ullamco mollit commodo esse Lorem ullamco nulla. Pariatur tempor velit voluptate reprehenderit excepteur deserunt ex laborum ullamco aliquip ex. Dolore duis velit sint deserunt pariatur adipisicing exercitation. Pariatur Lorem Lorem aliquip irure enim cupidatat veniam.

Sunt occaecat occaecat aliquip sit ad sit labore do esse quis anim. Deserunt nostrud culpa magna duis officia ipsum esse labore commodo. Duis do cillum exercitation nostrud tempor dolor. Do officia mollit laboris anim enim.

Mollit minim laborum est elit in. Aliqua reprehenderit mollit amet aliquip cillum voluptate ipsum est laboris ullamco duis consectetur ipsum Lorem. Enim anim duis occaecat anim sint eu aute consectetur proident consequat esse. Esse tempor irure cillum elit quis.

Commodo eiusmod cupidatat consequat exercitation proident occaecat sint Lorem excepteur esse esse. Officia officia dolor nostrud fugiat excepteur duis irure. Adipisicing pariatur culpa enim aute id labore excepteur sit sit magna consequat. Ipsum in eiusmod ipsum nostrud irure id sint commodo voluptate.

Nulla incididunt sit eiusmod ullamco voluptate ex est ad eu id Lorem fugiat. Occaecat laboris do dolor ex ad. Ea veniam nisi reprehenderit duis nisi exercitation nulla exercitation excepteur reprehenderit. Reprehenderit mollit sit consequat deserunt ea. Sunt laboris quis laboris duis adipisicing ea laborum aute cupidatat. Exercitation dolor commodo adipisicing tempor ipsum non amet mollit deserunt minim irure ut veniam. Sit sunt et quis deserunt ex aliqua elit eu excepteur commodo veniam.

Nostrud cupidatat nostrud consectetur cillum aliqua nisi in laborum. Aute occaecat nostrud nisi consequat aute non consequat consectetur. Ea Lorem cillum irure deserunt labore qui labore dolor voluptate. Sit id tempor est fugiat Lorem. Nulla dolore pariatur reprehenderit occaecat eu excepteur nulla et consequat aliqua magna. Consequat magna aliqua irure nulla minim culpa excepteur. Nulla non non excepteur eiusmod ipsum in deserunt laborum minim aliqua cupidatat quis nostrud.

Est irure proident ut ex dolor esse esse mollit fugiat ad ad enim ut. Mollit sit aute consequat in aute duis commodo sunt. Eiusmod dolor consectetur esse consectetur eu excepteur laboris proident do occaecat nulla occaecat. Pariatur minim consectetur ea Lorem ea. Elit ullamco consequat sit occaecat amet dolore quis."""
            ),
        )

        try:
            while self.server.running:
                server_network_process(self.world, self.server)
                movement_process(self.world)
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
