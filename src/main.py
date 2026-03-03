import pygame
from core.environment import Environment
from rendering.game_renderer import GameRenderer


def main():

    env = Environment()
    renderer = GameRenderer()

    running = True

    while running:

        renderer.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    env.reset()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()

        action = {
            "accelerate": keys[pygame.K_w],
            "brake": keys[pygame.K_s],
            "left": keys[pygame.K_a],
            "right": keys[pygame.K_d],
        }

        env.step(action)
        renderer.render(env)

    pygame.quit()


if __name__ == "__main__":
    main()