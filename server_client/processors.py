import pygame
from dinobytes import unpackd
from phecs import World

from server_client.components import Position, Timer, Velocity
from server_client.mod import GameClient, GameServer
from server_client.types import (
    ClientChatMessage,
    ClientConnectRequest,
    ClientConnectResponse,
    GameState,
)


def movement_process(world: World):
    for _, pos, vel in world.find(Position, Velocity):
        pos.x += vel.x
        pos.y += vel.y


def timer_process(world: World, dt: float):
    for ent, timer in world.find(Timer):
        timer.time += dt
        if timer.time > timer.interval:
            timer.callback()
            timer.time = 0
            if not timer.repeat:
                world.remove(ent, Timer)


def server_network_process(world: World, server: GameServer):
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


def client_network_process(state: GameState, client: GameClient):
    if not state.connected and client.connected:
        state.connected = True
        client.send_message(bytes(ClientConnectRequest()))

    for msg in client.get_messages():
        message = unpackd(msg)
        match message:
            case GameState(components):  # type: ignore
                for ent_comps in components:
                    for component in ent_comps:
                        print(f"Received component: {component}")


def input_process(client: GameClient):
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


def render_process(screen: pygame.Surface, world: World):
    screen.fill((0, 0, 0))
    for _, pos in world.find(Position):
        pygame.draw.circle(screen, (255, 255, 255), (pos.x, pos.y), 4)
    pygame.display.flip()
