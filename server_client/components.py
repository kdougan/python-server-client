from dataclasses import dataclass
from typing import Callable

from dinobytes import dbyte


@dbyte
@dataclass
class Ent:
    value: int = 0


@dbyte
@dataclass
class Size:
    width: float
    height: float


@dbyte
@dataclass
class Position:
    x: float
    y: float


@dbyte
@dataclass
class Velocity:
    x: float
    y: float


@dbyte
class Immobile:
    pass


@dbyte
@dataclass
class Sprite:
    image_path: str


@dbyte
@dataclass
class Collider:
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0


@dbyte
@dataclass
class Health:
    value: int


@dbyte
@dataclass
class Score:
    value: int


@dbyte
@dataclass
class Shape:
    shape: str
    color: str


@dbyte
@dataclass
class Timer:
    interval: float
    repeat: bool
    callback: Callable
    time: float = 0.0


@dbyte
@dataclass
class PendingAck:
    ttl: float = 1.0


@dbyte
@dataclass
class Message:
    message: str


@dbyte
@dataclass
class Player:
    value: str
