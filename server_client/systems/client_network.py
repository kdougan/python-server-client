from dinobytes import unpackd
from phecs import World

from server_client.components import Ent
from server_client.mod import GameClient
from server_client.types import (
    ClientConnectResponse,
    DespawnEntity,
    GameState,
    SpawnEntity,
    State,
    UpdateEntity,
)


def client_network_sys(client: GameClient, world: World, state: State):
    for msg in client.get_messages():
        message = unpackd(msg)
        match message:
            case ClientConnectResponse(id):  # type: ignore
                print(f"Connected to server with id: {id}")
                state.client_id = id

            case SpawnEntity(components):  # type: ignore
                print("Spawning entity")
                world.spawn(*components)

            case UpdateEntity(ent, components):  # type: ignore
                for e, ent_ in world.find(Ent):
                    if ent_ == ent:
                        for component in components:
                            world.insert(e, component)

            case DespawnEntity(ent):  # type: ignore
                print(f"Despawning entity: {ent}")
                for _, ent_ in world.find(Ent):
                    if ent_ == ent:
                        world.despawn(ent_)

            case GameState(components):  # type: ignore
                world.clear()
                for ent_comps in components:
                    ent = world.spawn()
                    for component in ent_comps:
                        world.insert(ent, component)

            case _:
                print(f"Unknown message: {message}")
