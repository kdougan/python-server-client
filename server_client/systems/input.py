import pygame
from phecs import World

from server_client.components import Ent, Position
from server_client.mod import GameClient
from server_client.types import ClientChatMessage, ClientMoveRequest, State


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
                pos.y -= 10 * state.dt
        client.send_message(bytes(ClientMoveRequest(0, -10)))
    elif pygame.key.get_pressed()[pygame.K_DOWN]:
        for _, pos, ent in world.find(Position, Ent):
            if ent.value == state.client_id:
                pos.y += 10 * state.dt
        client.send_message(bytes(ClientMoveRequest(0, 10)))
