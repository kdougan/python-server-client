import time
from typing import Any

from dinobytes import unpackd
from phecs import Entity, World

from server_client.mod import GameClient
from server_client.types import (
    ClientConnectResponse,
    ClientState,
    DespawnEntity,
    GameState,
    ServerTimeResponse,
    SpawnEntity,
    UpdateEntity,
)


def client_network_sys(client: GameClient, world: World, state: ClientState):
    for msg in client.get_messages():
        message = unpackd(msg)
        match message:
            case ClientConnectResponse(id):  # type: ignore
                handle_client_connect(state, id)
            case SpawnEntity(entity_id, components, local_ent):  # type: ignore
                handle_spawn_entity(world, entity_id, components, state, local_ent)
            case UpdateEntity(entity_id, components):  # type: ignore
                handle_update_entity(world, entity_id, components)
            case DespawnEntity(entity_id):  # type: ignore
                handle_despawn_entity(world, entity_id)
            case GameState(entities):  # type: ignore
                handle_game_state(world, entities, state)
            case ServerTimeResponse(ts):  # type: ignore
                handle_server_time(state, ts)
            case _:
                print(f"Unknown message: {message}")


def handle_server_time(state: ClientState, ts: float):
    send_time = state.last_sync_send_time
    receive_time = time.time()
    server_time = ts
    rtt = receive_time - send_time
    offset = (server_time - (rtt * 0.5)) - receive_time
    state.game_clock = server_time + offset


def handle_game_state(world, entities: dict[int, list[Any]], state: ClientState):
    world.clear()
    state.server_ent_map.clear()
    for entity_id, components in entities.items():
        ent = world.spawn(components)
        state.server_ent_map[ent] = entity_id


def handle_despawn_entity(world, ent: int):
    print(f"Despawning entity: {ent}")
    world.despawn(ent)


def handle_update_entity(world, entity_id: int, components: list[Any]):
    entity = Entity(entity_id)
    for component in components:
        world.insert(entity, component)


def handle_spawn_entity(
    world: World,
    entity_id: int,
    components: list[Any],
    state: ClientState,
    local_ent: int | None = None,
):
    print("Spawning entity")
    ent = world.spawn(*components)
    state.server_ent_map[ent] = entity_id
    if local_ent:
        world.despawn(Entity(local_ent))


def handle_client_connect(state: ClientState, id: str):
    print(f"Connected to server with id: {id}")
    state.client_id = id
