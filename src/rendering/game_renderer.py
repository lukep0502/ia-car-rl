import pygame


class GameRenderer:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Car AI")

        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(None, 30)
        self.font_big = pygame.font.SysFont(None, 72)

    def render(self, env):
        self.screen.fill("black")

        # Track
        env.track.draw(self.screen)

        # Draw car
        self.draw_car(env.car)

        # Progress bar
        self._draw_progress(env)

        # UI
        self._draw_ui(env)

        pygame.display.flip()

    def _draw_progress(self, env):
        bar_width = 200
        bar_height = 20
        bar_x = self.width - bar_width - 20
        bar_y = 20

        pygame.draw.rect(self.screen, "white",
                         (bar_x, bar_y, bar_width, bar_height), 2)

        progress_ratio = env.total_progress / 360
        fill_width = bar_width * progress_ratio

        pygame.draw.rect(
            self.screen,
            "green",
            (bar_x, bar_y, fill_width, bar_height)
        )

    def _draw_ui(self, env):
        lap_text = self.font_small.render(
            f"Lap: {env.laps}/{env.max_laps}", True, "white")
        self.screen.blit(lap_text, (20, 20))

        time_text = self.font_small.render(
            f"Lap Time: {env.current_lap_time:.2f}s", True, "white")
        self.screen.blit(time_text, (20, 50))

        total_text = self.font_small.render(
            f"Total Time: {env.total_time:.2f}s", True, "white")
        self.screen.blit(total_text, (20, 80))

        if env.best_lap_time:
            best_text = self.font_small.render(
                f"Best: {env.best_lap_time:.2f}s", True, "yellow")
            self.screen.blit(best_text, (20, 110))

        if env.race_finished:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # Título principal
            text1 = self.font_big.render(
                "CORRIDA FINALIZADA", True, "white"
            )
            self.screen.blit(
                text1,
                text1.get_rect(center=(self.width // 2,
                                    self.height // 2 - 60))
            )

            # Instrução reiniciar
            text2 = self.font_small.render(
                "Pressione R para reiniciar", True, "yellow"
            )
            self.screen.blit(
                text2,
                text2.get_rect(center=(self.width // 2,
                                    self.height // 2))
            )

            # Instrução sair
            text3 = self.font_small.render(
                "Pressione ESC para sair", True, "lightgray"
            )
            self.screen.blit(
                text3,
                text3.get_rect(center=(self.width // 2,
                                    self.height // 2 + 40))
            )
    def draw_car(self, car):
        width = 40
        height = 20

        rect = pygame.Rect(0, 0, width, height)
        rect.center = (car.x, car.y)

        car_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        car_surface.fill((255, 0, 0))

        rotated = pygame.transform.rotate(car_surface, car.angle)
        rotated_rect = rotated.get_rect(center=rect.center)

        self.screen.blit(rotated, rotated_rect.topleft)