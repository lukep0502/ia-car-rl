import math
import pygame
from tracks.base_track import BaseTrack
WIDTH, HEIGHT = 800, 600

class CircularTrack(BaseTrack):
    def __init__(self):
        # Circle properties
        self.center = (WIDTH // 2, HEIGHT // 2)  # Center of the screen
        self.radius = 200                    # Radius in pixels                             
        self.thickness = 80                     # 0 = filled circle     

        # Finish line properties
        inner_radius = self.radius - self.thickness

        self.finish_line_x = self.center[0]

        self.finish_line_y1 = self.center[1] - self.radius
        self.finish_line_y2 = self.center[1] - inner_radius          

    def draw(self, surface):
        # Draw the circular track
        pygame.draw.circle(surface, "white", self.center, self.radius, self.thickness)

        # Draw finish line
        pygame.draw.line(
                surface,
                "red",
                (self.finish_line_x, self.finish_line_y1),
                (self.finish_line_x, self.finish_line_y2),
                3
            )

    def is_on_track(self, x, y):
        dx = x - self.center[0]
        dy = y - self.center[1]
        distance = math.sqrt(dx**2 + dy**2)

        outer_limit = self.radius
        inner_limit = self.radius - self.thickness

        return inner_limit < distance < outer_limit
    
    # Get the angle from the center of the track to a given point (x, y)
    def get_angle(self, x, y):
        dx = x - self.center[0]
        dy = self.center[1] - y  # invertido por causa do eixo do pygame
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360

    def crossed_finish_line(self, last_pos, current_pos):
            lx, ly = last_pos
            cx, cy = current_pos

            # Verifica se cruzou eixo X da linha
            crossed = (lx < self.finish_line_x and cx >= self.finish_line_x)

            # E está dentro da altura da linha
            inside_height = (
                self.finish_line_y1 <= cy <= self.finish_line_y2
            )

            return crossed and inside_height