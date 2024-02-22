import pygame
from dinobytes import unpackd
from phecs import World

from server_client.components import (
    Collider,
    Ent,
    Position,
    Shape,
    Size,
    Timer,
    Velocity,
)
from server_client.mod import GameClient, GameServer
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


def movement_system(world: World, state: GameState):
    for _, pos, vel in world.find(Position, Velocity):
        pos.x += vel.x * state.dt
        pos.y += vel.y * state.dt


def collision_system(world: World):
    def colliders_collide(colA, colB):
        return (
            colA.x < colB.x + colB.width
            and colA.x + colA.width > colB.x
            and colA.y < colB.y + colB.height
            and colA.y + colA.height > colB.y
        )

    for entA, posA, velA, colA in world.find(Position, Velocity, Collider):
        colA.x = posA.x
        colA.y = posA.y
        for entB, posB, colB in world.find(Position, Collider):
            if entA == entB:
                continue
            colB.x = posB.x
            colB.y = posB.y
            if colliders_collide(colA, colB):
                centerA_x = colA.x + colA.width / 2
                centerA_y = colA.y + colA.height / 2
                centerB_x = colB.x + colB.width / 2
                centerB_y = colB.y + colB.height / 2

                diff_x = centerA_x - centerB_x
                diff_y = centerA_y - centerB_y

                overlap_x = colA.width / 2 + colB.width / 2 - abs(diff_x)
                overlap_y = colA.height / 2 + colB.height / 2 - abs(diff_y)

                if overlap_x < overlap_y:
                    velA.x *= -1
                    if diff_x > 0:
                        posA.x += overlap_x
                    else:
                        posA.x -= overlap_x
                else:
                    velA.y *= -1
                    if diff_y > 0:
                        posA.y += overlap_y
                    else:
                        posA.y -= overlap_y


def timer_system(world: World, dt: float):
    for ent, timer in world.find(Timer):
        timer.time += dt
        if timer.time > timer.interval:
            timer.callback()
            timer.time = 0
            if not timer.repeat:
                world.remove(ent, Timer)


def server_network_system(world: World, server: GameServer, state: State):
    def handle_client_connect(server: GameServer, client_id: str, state: State):
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

    for msg in server.get_messages():
        client_id, message = msg.client_id, unpackd(msg.data)
        match message:
            case ClientConnectRequest():  # type: ignore
                print(f"Client {client_id} connected")
                handle_client_connect(server, client_id, state)

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


def client_network_system(client: GameClient, world: World, state: State):
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


def input_system(client: GameClient, world: World, state: State):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_SPACE:
                print("Space pressed")
                client.send_message(bytes(ClientChatMessage("space pressed")))

    if pygame.key.get_pressed()[pygame.K_UP]:
        for _, pos, ent in world.find(Position, Ent):
            if ent.value == state.client_id:
                pos.y -= 10 * state.dt
        client.send_message(bytes(ClientMoveRequest(0, -10)))
    elif pygame.key.get_pressed()[pygame.K_DOWN]:
        for _, pos, ent in world.find(Position, Ent):
            if ent.value == state.client_id:
                pos.y += 10 * state.dt
        client.send_message(bytes(ClientMoveRequest(0, 10)))


def render_system(screen: pygame.Surface, world: World):
    screen.fill((20, 30, 20))
    for _, pos, size, shape in world.find(Position, Size, Shape):
        if shape.shape == "square":
            pygame.draw.rect(
                screen,
                pygame.Color(shape.color),
                (pos.x, pos.y, size.width, size.height),
            )
    pygame.display.flip()
