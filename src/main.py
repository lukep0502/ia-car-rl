import os
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
from ai.trainer import Trainer
from core.environment import Environment
from rendering.game_renderer import GameRenderer
from ai.agent import Agent
from tracks.track1 import Track1
from tracks.circular_track import CircularTrack

WIDTH, HEIGHT = 800, 800


def main():

    mode = input("Modo IA? (s/n): ").strip().lower()
    ia = mode == "s"
    agent = None
    env = None
    
    if ia == True:
        track = Track1(WIDTH, HEIGHT)
        env = Environment(WIDTH, HEIGHT, track)
        env.reset()  # Initialize environment state
        agent = Agent()

        use_model = input("Usar modelo salvo? (s/n): ").lower()

        if use_model == "s":

            version = input("Qual versão? (ex: v1): ")

            agent.load(version)
            env.reset()
            agent.apply_model_stats(env)

        else:
            print("Treinando do zero.")

            trainer = Trainer(env, agent)
            trainer.train(10000)
            env = trainer.env
            env.reset()
            agent.set_model_stats(trainer.export_stats())
            agent.apply_model_stats(env)
            save_model = input("Salvar modelo? (s/n): ").lower()
            result = input("Ver resultado? (s/n): ").lower()
            if save_model == "s":

                version = input("Nome da versão (ex: v1, v2, teste1): ")

                agent.save(version)

            # Headless training mode for performance.
            if result != "s":
                return

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    if env is None:
        track = Track1(WIDTH, HEIGHT)
        env = Environment(WIDTH, HEIGHT, track)
        env.reset()


    running = True

    renderer = GameRenderer(WIDTH, HEIGHT)

    while running:

        renderer.clock.tick(60)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and not ia:
                    env.reset()
                if event.key == pygame.K_q and ia:
                    env.debug = not env.debug
                    print("Debug mode:", env.debug)

        if ia:
            state = env.get_state()
            action_index = agent.act(state)
            action = agent.action_to_dict(action_index)
        else:
            keys = pygame.key.get_pressed()
            action = {
                "accelerate": keys[pygame.K_w],
                "brake": keys[pygame.K_s],
                "left": keys[pygame.K_a],
                "right": keys[pygame.K_d],
            }

        if ia == True:
            next_state, reward, done = env.step(action)
            agent.learn(state, action_index, reward, next_state, done)
            if done:
                env.reset()
        else:
            env.step(action)

        renderer.render(env, ia, agent if ia else None)

    pygame.quit()


if __name__ == "__main__":
    main()
