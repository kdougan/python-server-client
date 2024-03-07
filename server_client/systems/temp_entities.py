from phecs import World

from server_client.components import PendingAck
from server_client.types import State


def temp_entities_sys(world: World, state: State):
    for ent, pending in world.find(PendingAck):
        pending.ttl -= state.dt
        if pending.ttl <= 0:
            world.despawn(ent)
