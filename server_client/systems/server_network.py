import time

from dinobytes import unpackd
from phecs import World

from server_client.components import Collider, Ent, Position, Shape, Size, Velocity
from server_client.mod import GameServer
from server_client.types import (
    ClientChatMessage,
    ClientConnectRequest,
    ClientConnectResponse,
    ClientDisconnect,
    ClientMoveRequest,
    DespawnEntity,
    GameState,
    ServerState,
    ServerTimeRequest,
    SpawnEntity,
    UpdateEntity,
)


def server_network_sys(world: World, server: GameServer, state: ServerState):
    for msg in server.get_messages():
        client_id, message = msg.client_id, unpackd(msg.data)
        match message:
            case ClientConnectRequest():  # type: ignore
                handle_client_connect(server, client_id, world, state)
            case ClientMoveRequest(x, y):  # type: ignore
                handle_client_move(world, server, state, client_id, x, y)
            case ClientChatMessage(message):  # type: ignore
                print(f"Client sent message: {message}")
            case ClientDisconnect():  # type: ignore
                print(f"Client {client_id} disconnected")
                handle_client_disconnect(world, server, state, client_id)
            case ServerTimeRequest():  # type: ignore
                handle_server_time(server, client_id)
            case _:
                print(f"Unknown message: {message}")


def handle_server_time(server, client_id):
    server.send_message(
        client_id,
        bytes(ServerTimeRequest(ts=time.time())),
    )


def handle_client_disconnect(world, server, state, client_id):
    world.despawn(state.players[client_id])
    server.broadcast(
        bytes(DespawnEntity(state.players[client_id])),
        without=[client_id],
    )
    del state.players[client_id]


def handle_client_move(world, server, state, client_id, x, y):
    if client_id in state.players:
        id_ = state.players[client_id]
        for _, pos, ent in world.find_on(id_, Position, Ent):
            pos.x += x
            pos.y += y
            server.broadcast(bytes(UpdateEntity(ent, [pos])), without=[client_id])

    return _


def handle_client_connect(
    server: GameServer, client_id: str, world: World, state: ServerState
):
    print(f"Client {client_id} connected")
    if len(state.players) < 2:
        player_num = len(state.players)
        # create the paddle
        components = [
            Ent(client_id),
            Position(x=20 if player_num == 0 else 760, y=300),
            Size(width=20, height=100),
            Velocity(x=0, y=0),
            Collider(x=20 if player_num == 0 else 760, y=300, width=20, height=100),
            Shape(shape="square", color="white"),
        ]
        state.players[client_id] = world.spawn(*components)
        server.send_message(client_id, bytes(ClientConnectResponse(client_id)))
        server.broadcast(bytes(SpawnEntity(components)), without=[client_id])
        send_game_state(server, client_id, world)


def send_game_state(server: GameServer, client_id: str, world: World):
    state = GameState(
        entities={entity.__id: components for entity, components in world.iter_every()}
    )
    print(f"Sending game state: {state}")
    server.send_message(client_id, bytes(state))  # type: ignore
