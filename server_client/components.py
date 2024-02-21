from dataclasses import dataclass
from typing import Callable

from dinobytes import dbyte
from glm import vec2


@dbyte
@dataclass
class Ent:
    value: int = 0


@dbyte
class Position(vec2):
    pass


@dbyte
class Velocity(vec2):
    pass


@dataclass
class Sprite:
    image_path: str


@dbyte
class Collider(vec2):
    pass


@dbyte
@dataclass
class Health(int):
    pass


@dbyte
@dataclass
class Score(int):
    pass


@dataclass
class Shape:
    shape: str
    color: str
    size: vec2


@dataclass
class Timer:
    interval: float
    repeat: bool
    callback: Callable
    time: float = 0.0


@dataclass
class Blackboard:
    dt: float


@dataclass
class Ephemeral:
    timeout: float = 1.0


@dbyte
@dataclass
class Message:
    message: str
