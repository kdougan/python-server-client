from __future__ import annotations

from dataclasses import dataclass, field

from dinobytes import dbyte


@dataclass
class ClientState:
    connected: bool = False
    dt: float = 0.0


@dataclass
class ServerState:
    dt: float = 0.0


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
