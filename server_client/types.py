from dataclasses import dataclass
from dinobytes import networkmessage


@dataclass
class Blackboard:
    dt: float = 0.0


@networkmessage
class ClientConnect:
    address: tuple[str, int]


@networkmessage
class ClientDisconnect:
    pass


@networkmessage
class ClientChatMessage:
    message: str


@networkmessage
class CreateEntity:
    type: str
