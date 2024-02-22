from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dinobytes import dbyte
from phecs import Entity


@dataclass
class State:
    dt: float = 0.0
    client_id: str = ""
    players: dict[str, Entity] = field(default_factory=dict)


@dbyte
@dataclass
class GameState:
    components: dict[int, dict[str, str]] = field(default_factory=dict)


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
    components: list[Any] = field(default_factory=list)


@dbyte
@dataclass
class UpdateEntity:
    ent_id: str
    components: list[Any] = field(default_factory=list)


@dbyte
@dataclass
class DespawnEntity:
    ent_id: str
