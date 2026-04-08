import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from ai.agent import Agent
from ai.trainer import Trainer
from core.environment import Environment
from menu.menu import track_menu
from rendering.game_renderer import GameRenderer
from tracks.circular_track import CircularTrack
from tracks.oval_track import OvalTrack
from tracks.track1 import Track1

WIDTH, HEIGHT = 800, 800
TRAINING_TRACK = Track1


def menu():
    track = track_menu()
    # Circular Track
    if track == 1:
        track = CircularTrack(WIDTH, HEIGHT)
        best_model = "vBestVersionCircular"
    # Oval Track
    if track == 2:
        track = OvalTrack(WIDTH, HEIGHT)
        best_model = "vBestVersionOval"
    # First Track
    if track == 3:
        track = Track1(WIDTH, HEIGHT)
        best_model = "vBestVersionTrack1"

    return track, best_model


def main():
    track, best_model = menu()
    mode = input("AI mode? (y/n): ").strip().lower()
    ia = mode == "y"
    use_model = "n"
    agent = None
    env = None

    if ia is True:
        env = Environment(WIDTH, HEIGHT, track)
        env.reset()  # Initialize environment state
        agent = Agent()

        use_best_model = input("Do you want to use the best model? (y/n): ").lower()

        if use_best_model == "y":
            agent.load(best_model)
            env.reset()
            agent.apply_model_stats(env)
        else:
            use_model = input("Use saved model? (y/n): ").lower()

        if use_model == "y" and use_best_model != "y":
            version = input("Which version? (e.g. v1): ")

            agent.load(version)
            env.reset()
            agent.apply_model_stats(env)

        if use_model == "n" and use_best_model != "y":
            print("Training from scratch.")

            trainer = Trainer(env, agent)
            trainer.train(15000)
            env = trainer.env
            env.reset()
            agent.set_model_stats(trainer.export_stats())
            agent.apply_model_stats(env)
            save_model = input("Save model? (y/n): ").lower()
            result = input("See result? (y/n): ").lower()
            if save_model == "y":
                version = input("Version name (e.g. v1, v2, test1): ")
                agent.save(version)

            # Headless training mode for performance.
            if result != "y":
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

        if ia is True:
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
