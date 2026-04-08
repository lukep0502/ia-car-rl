import math

import pygame


class GameRenderer:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Car AI")

        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont(None, 30)
        self.font_big = pygame.font.SysFont(None, 72)
        self.neutral_bg = (125, 125, 125)
        self.panel_color = (68, 68, 68, 190)
        self.text_color = (245, 245, 245)
        self.muted_text = (220, 220, 220)
        self.highlight_color = (255, 220, 120)

    def render(self, env, ia, agent=None):
        self.screen.fill(self.neutral_bg)

        if env.track.type == "image-based":
            self.display_track(env)
        else:
            self.screen.fill(self.neutral_bg)

        # Track
        if env.track.type == "procedural":
            env.track.draw_track(self.screen)
            if env.debug:
                env.track.draw_checkpoints(self.screen, env.progress_state)

        # Draw car
        self.draw_car(env.car)

        if ia and env.sensor_points and env.debug:
            self.draw_sensors(env, self.screen, env.sensor_points)

        # Progress bar
        self._draw_progress(env)

        # Debug checkpoint and start line
        if env.track.type == "image-based" and env.debug:
            self.debug_draw(env)

        # UI
        self._draw_ui(env, ia)

        if ia and env.debug:
            self._draw_debug_overlay(env, agent)
            self._draw_diagnostic_overlay(env)

        pygame.display.flip()

    def _draw_progress(self, env):
        env.track._draw_progress(self.screen, env)

    def debug_draw(self, env):
        env.track.draw_debug(self.screen)

    def _draw_ui(self, env, ia):
        self._draw_panel(12, 12, 250, 130 if env.best_lap_time else 100)

        lap_text = self.font_small.render(
            f"Lap: {env.laps}/{env.max_laps}", True, self.text_color
        )
        self.screen.blit(lap_text, (20, 20))

        time_text = self.font_small.render(
            f"Lap Time: {env.current_lap_time:.2f}s", True, self.muted_text
        )
        self.screen.blit(time_text, (20, 50))

        total_text = self.font_small.render(
            f"Total Time: {env.total_time:.2f}s", True, self.muted_text
        )
        self.screen.blit(total_text, (20, 80))

        if env.best_lap_time:
            best_text = self.font_small.render(
                f"Best: {env.best_lap_time:.2f}s", True, self.highlight_color
            )
            self.screen.blit(best_text, (20, 110))

        if env.race_finished:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # Main title
            text1 = self.font_big.render("RACE FINISHED", True, self.text_color)
            self.screen.blit(
                text1,
                text1.get_rect(center=(self.width // 2, self.height // 2 - 60)),
            )

            # Restart instruction
            restart_msg = "Press R to restart" if not ia else "AI: automatic restart"
            text2 = self.font_small.render(
                restart_msg, True, self.highlight_color
            )
            self.screen.blit(
                text2,
                text2.get_rect(center=(self.width // 2, self.height // 2)),
            )

            # Exit instruction
            text3 = self.font_small.render(
                "Press ESC to exit", True, self.muted_text
            )
            self.screen.blit(
                text3,
                text3.get_rect(center=(self.width // 2, self.height // 2 + 40)),
            )

    def _draw_debug_overlay(self, env, agent=None):
        """Overlay with runtime debugging and training stats."""
        self._draw_panel(10, 10, 330, 228)

        lines = []
        lines.append("--- CURRENT RUN ---")
        lines.append(f"Episode: {getattr(env, 'current_episode', 'N/A')}")
        epsilon = getattr(agent, "epsilon", None) if agent else None
        lines.append(
            f"Epsilon: {epsilon:.3f}" if isinstance(epsilon, (int, float)) else "Epsilon: N/A"
        )
        lines.append(f"Episode Reward: {getattr(env, 'current_episode_reward', 0):.1f}")
        lines.append(f"Distance: {getattr(env, 'current_distance', 0):.1f}")

        lines.append("--- BEST RESULTS ---")
        lines.append(f"Best Reward: {self._format_value(getattr(env, 'best_reward_ever', None), 1)}")
        lines.append(
            f"Best Lap Time: {self._format_value(getattr(env, 'best_lap_time_ever', None), 2, suffix='s')}"
        )
        lines.append(
            f"Best Progress: {self._format_value(getattr(env, 'longest_distance', None), 1, suffix='%')}"
        )

        if getattr(env, "benchmark_history", None):
            last = env.benchmark_history[-1]
            lines.append("--- LAST 5000 EPISODES ---")
            lines.append(f"Best R: {self._format_value(last.get('best_reward'), 1)}")
            lines.append(f"Best Lap: {self._format_value(last.get('best_lap_time'), 2, suffix='s')}")
            lines.append(f"Laps: {self._format_value(last.get('total_laps'), 1)}")

        y = 18
        for line in lines:
            txt = self.font_small.render(line, True, self.text_color)
            self.screen.blit(txt, (20, y))
            y += 18

    def _draw_diagnostic_overlay(self, env):
        """Diagnostic metrics overlay in bottom left corner."""
        panel_height = 20 + 7 * 20
        self._draw_panel(10, self.height - panel_height - 10, 310, panel_height)
        lines = [
            f"Forward Progress: {getattr(env, 'forward_progress_rate', 0):.2f}",
            f"Wall Proximity: {getattr(env, 'wall_proximity_rate', 0):.2f}",
            f"Exploration Diversity: {getattr(env, 'exploration_diversity', 0):.2f}",
            f"Stuck Rate: {getattr(env, 'stuck_rate', 0):.2f}",
            f"Track Progress: {getattr(env, 'track_completion_progress', 0):.2f}",
            f"Episode Survival: {getattr(env, 'episode_survival_time', 0):.1f}",
            f"Progress Efficiency: {getattr(env, 'progress_efficiency', 0):.3f}",
        ]

        y = self.height - 20 - len(lines) * 20  # Start from bottom, 20px per line
        for line in lines:
            txt = self.font_small.render(line, True, self.text_color)
            self.screen.blit(txt, (20, y))
            y += 20

    def draw_car(self, car):
        width = 30
        height = 15

        rect = pygame.Rect(0, 0, width, height)
        rect.center = (car.x, car.y)

        car_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        car_surface.fill((255, 0, 0))

        rotated = pygame.transform.rotate(car_surface, car.angle)
        rotated_rect = rotated.get_rect(center=rect.center)

        self.screen.blit(rotated, rotated_rect.topleft)

    def display_track(self, env):
        self.screen.blit(env.track.image, (0, 0))

    def _draw_panel(self, x, y, width, height):
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill(self.panel_color)
        self.screen.blit(overlay, (x, y))

    def _format_value(self, value, decimals=1, suffix=""):
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            if isinstance(value, float) and not math.isfinite(value):
                return "N/A"
            return f"{value:.{decimals}f}{suffix}"
        return str(value)

    # Draw car sensors
    def draw_sensors(self, env, screen, sensor_points):
        car_pos = (int(env.car.x), int(env.car.y))

        for point in sensor_points:
            px = int(point[0])
            py = int(point[1])

            pygame.draw.line(
                screen,
                (0, 255, 0),
                car_pos,
                (px, py),
                2,
            )

            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (px, py),
                4,
            )
