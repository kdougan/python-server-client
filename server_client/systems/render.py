from glm import vec2
import pygame
from phecs import World

from server_client.components import Paddle, Position, Shape, Size


def render_sys(screen: pygame.Surface, world: World, font: pygame.font.Font):
    screen.fill((20, 30, 20))
    for _, pos, size, shape in world.find(Position, Size, Shape):
        if shape.shape == "square":
            pygame.draw.rect(
                screen,
                pygame.Color(shape.color),
                (pos.x, pos.y, size.width, size.height),
            )

    # print the paddle position above the paddle
    for _, pos in world.find(Position, has=Paddle):
        text = font.render(f"{pos.y}", True, (255, 255, 255))
        screen_center = screen.get_rect().center
        # pos is halfway to center from paddle
        p = vec2(pos.x, pos.y)
        c = vec2(screen_center[0], screen_center[1])

        np = (c * 2 + p) / 2 - c / 2.0
        screen.blit(text, (np.x, np.y))

    pygame.display.flip()
