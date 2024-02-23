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
    SpawnEntity,
    State,
    UpdateEntity,
)


def server_network_sys(world: World, server: GameServer, state: State):
    for msg in server.get_messages():
        client_id, message = msg.client_id, unpackd(msg.data)
        match message:
            case ClientConnectRequest():  # type: ignore
                print(f"Client {client_id} connected")
                handle_client_connect(server, client_id, world, state)

            case ClientMoveRequest(x, y):  # type: ignore
                if client_id in state.players:
                    id_ = state.players[client_id]
                    for _, pos, ent in world.find_on(id_, Position, Ent):
                        pos.x += x
                        pos.y += y
                        server.broadcast_to_all_except(
                            client_id, bytes(UpdateEntity(ent, [pos]))
                        )

            case ClientChatMessage(message):  # type: ignore
                print(f"Client sent message: {message}")

            case ClientDisconnect():  # type: ignore
                print(f"Client {client_id} disconnected")
                world.despawn(state.players[client_id])
                server.broadcast_to_all_except(
                    client_id, bytes(DespawnEntity(state.players[client_id]))
                )
                del state.players[client_id]

            case _:
                print(f"Unknown message: {message}")


def handle_client_connect(
    server: GameServer, client_id: str, world: World, state: State
):
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
        server.send_message_to_client(
            client_id, bytes(ClientConnectResponse(client_id))
        )
        server.broadcast_to_all_except(client_id, bytes(SpawnEntity(components)))
        send_game_state(server, client_id, world)


def send_game_state(server: GameServer, client_id: str, world: World):
    state = GameState(components=[c for _, c in world.iter_every()])
    print(f"Sending game state: {state}")
    server.send_message_to_client(client_id, bytes(state))  # type: ignore
