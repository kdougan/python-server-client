from dataclasses import dataclass
from typing import Callable
from glm import vec2


@dataclass
class Ent(int):
    pass


@dataclass
class Position(vec2):
    pass


@dataclass
class Velocity(vec2):
    pass


@dataclass
class Sprite:
    image_path: str


@dataclass
class Collider(vec2):
    pass


@dataclass
class Health(int):
    pass


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
