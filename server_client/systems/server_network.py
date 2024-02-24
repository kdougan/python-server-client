from dinobytes import unpackd
from phecs import World

from server_client.components import (
    Collider,
    Ent,
    Paddle,
    Position,
    Shape,
    Size,
    Velocity,
)
from server_client.lib import find
from server_client.mod import GameServer
from server_client.types import (
    ClientChatMessage,
    ClientConnectRequest,
    ClientConnectResponse,
    ClientDisconnect,
    ClientMoveRequest,
    DespawnEntity,
    GameState,
    RemoveComponents,
    SpawnEntity,
    State,
    UpdateEntity,
    RespondStateForSync,
)


def server_network_sys(world: World, server: GameServer, state: State):
    for msg in server.get_messages():
        client_id, message = msg.client_id, unpackd(msg.data)
        match message:
            case ClientConnectRequest():  # type: ignore
                print(f"Client {client_id} connected")
                handle_client_connect(server, client_id, world, state)

            case ClientMoveRequest(x, y):  # type: ignore
                print(f"Client {client_id} sent move request: {x}, {y}")
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

            case RespondStateForSync(state):  # type: ignore
                print(f"got sync state")
                # iterate through each synced entity and its state,
                # if discrepancy greater than threshold,
                # send local version of state for that entity to client

                local_entities = {}
                for _, components in world.iter_every():
                    if ent := find(Ent, components):
                        local_entities[ent.value] = {type(c): c for c in components}

                foreign_entities = {}
                for ent_id, components in state:
                    foreign_entities[ent.value] = {type(c): c for c in components}

                for ent_id, foreign_components in state:

                    local_components = local_entities.get(ent_id, None)
                    if local_components is None:
                        server.send_message_to_client(
                            client_id, bytes(DespawnEntity(ent_id))
                        )
                    else:
                        update = []
                        remove = []
                        for foreign_component in foreign_components:
                            if foreign_component not in local_components:
                                remove.append(type(foreign_component))

                            local_component = local_components[foreign_component]
                            # check all members of component
                            for (
                                attr,
                                foreign_value,
                            ) in foreign_component.__dict__.items():
                                local_value = local_component.__dict__[attr]
                                # if its a number, then only add to update if threshold is exceeded
                                if isinstance(foreign_value, (int, float)):
                                    if abs(foreign_value - local_value) > 0.1:
                                        update.append(local_component)
                                else:
                                    if foreign_value != local_value:
                                        update.append(local_component)

                        if update:
                            server.send_message_to_client(
                                client_id, bytes(UpdateEntity(ent_id, components))
                            )
                        if remove:
                            server.send_message_to_client(
                                client_id, bytes(RemoveComponents(ent_id, remove))
                            )

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
            Paddle(),
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
