import pygame
from dinobytes import unpackd
from phecs import World

from server_client.components import Collider, Position, Shape, Size, Timer, Velocity
from server_client.mod import GameClient, GameServer
from server_client.types import (
    ClientChatMessage,
    ClientConnectRequest,
    ClientConnectResponse,
    GameState,
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
        for entB, posB, colB in world.find(Position, Collider, without=Velocity):
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


def server_network_system(world: World, server: GameServer):
    def handle_client_connect(server: GameServer, client_id: str):
        server.send_message_to_client(
            client_id, bytes(ClientConnectResponse(client_id))
        )

    def send_game_state(server: GameServer, client_id: str, world: World):
        state = GameState(components=[c for _, c in world.iter_every()])
        print(f"Sending game state: {state}")
        server.send_message_to_client(client_id, bytes(state))  # type: ignore

    for msg in server.get_messages():
        client_id, message = msg.client_id, unpackd(msg.data)
        print(f"Server received message: {message}")
        match message:
            case ClientConnectRequest():  # type: ignore
                print(f"Client {client_id} connected")
                handle_client_connect(server, client_id)
                send_game_state(server, client_id, world)
            case ClientChatMessage(message):  # type: ignore
                print(f"Client sent message: {message}")
            case _:
                print(f"Unknown message: {message}")


def client_network_system(client: GameClient, world: World):
    for msg in client.get_messages():
        message = unpackd(msg)
        match message:
            case GameState(components):  # type: ignore
                world.clear()
                for ent_comps in components:
                    ent = world.spawn()
                    for component in ent_comps:
                        world.insert(ent, component)


def input_system(client: GameClient):
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
