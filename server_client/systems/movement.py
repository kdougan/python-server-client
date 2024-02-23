from phecs import World

from server_client.components import Position, Velocity
from server_client.types import State


def movement_sys(world: World, state: State):
    for _, pos, vel in world.find(Position, Velocity):
        pos.x += vel.x * state.dt
        pos.y += vel.y * state.dt
