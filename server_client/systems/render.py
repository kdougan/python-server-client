import pygame
from phecs import World

from server_client.components import Position, Shape, Size


def render_sys(screen: pygame.Surface, world: World):
    screen.fill((20, 30, 20))
    for _, pos, size, shape in world.find(Position, Size, Shape):
        if shape.shape == "square":
            pygame.draw.rect(
                screen,
                pygame.Color(shape.color),
                (pos.x, pos.y, size.width, size.height),
            )
    pygame.display.flip()
