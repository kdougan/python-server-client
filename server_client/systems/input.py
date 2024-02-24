import pygame
from phecs import World

from server_client.components import Ent, Position
from server_client.mod import GameClient
from server_client.types import ClientChatMessage, ClientMoveRequest, State

DEFAULT_VEL = 50.0


def input_sys(client: GameClient, world: World, state: State):
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
                pos.y -= DEFAULT_VEL * state.dt
        client.send_message(bytes(ClientMoveRequest(0, -DEFAULT_VEL * state.dt)))
        print(f"Sending move request: 0, {-DEFAULT_VEL}")
    elif pygame.key.get_pressed()[pygame.K_DOWN]:
        for _, pos, ent in world.find(Position, Ent):
            if ent.value == state.client_id:
                pos.y += DEFAULT_VEL * state.dt
        client.send_message(bytes(ClientMoveRequest(0, DEFAULT_VEL * state.dt)))
        print(f"Sending move request: 0, {-DEFAULT_VEL}")
