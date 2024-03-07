import pygame
from phecs import World

from server_client.components import Position, Shape, Size
from server_client.types import State


def render_sys(
    screen: pygame.Surface, font: pygame.font.Font, world: World, state: State
):
    screen.fill((20, 30, 20))
    for _, pos, size, shape in world.find(Position, Size, Shape):
        if shape.shape == "square":
            pygame.draw.rect(
                screen,
                pygame.Color(shape.color),
                (pos.x, pos.y, size.width, size.height),
            )

    text = font.render(f"Game Time: {state.game_clock:.2f}", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    pygame.display.flip()
