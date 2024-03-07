from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dinobytes import dbyte
from phecs import Entity
import time


@dataclass
class State:
    dt: float = 0.0
    game_clock: float = field(default_factory=time.time)


@dataclass
class ServerState(State):
    players: dict[str, Entity] = field(default_factory=dict)
    client_ent_map: dict[int, Entity] = field(default_factory=dict)


@dataclass
class ClientState(State):
    client_id: str = ""
    last_sync: float = 0.0
    last_sync_send_time: float = 0.0
    server_ent_map: dict[Entity, int] = field(default_factory=dict)


@dbyte
@dataclass
class GameState:
    entities: dict[int, list[Any]] = field(default_factory=dict)


@dbyte
class ClientConnectRequest:
    pass


@dbyte
@dataclass
class ClientConnectResponse:
    id: str


@dbyte
@dataclass
class ClientDisconnect:
    pass


@dbyte
@dataclass
class ClientChatMessage:
    message: str


@dbyte
@dataclass
class CreateEntity:
    type: str


@dbyte
@dataclass
class ClientMoveRequest:
    x: int
    y: int


@dbyte
@dataclass
class SpawnEntity:
    entity_id: int
    components: list[Any] = field(default_factory=list)
    local_ent: int | None = None


@dbyte
@dataclass
class UpdateEntity:
    entity_id: int
    components: list[Any] = field(default_factory=list)


@dbyte
@dataclass
class DespawnEntity:
    entity_id: int


@dbyte
class ServerTimeRequest:
    pass


@dbyte
@dataclass
class ServerTimeResponse:
    ts: float
