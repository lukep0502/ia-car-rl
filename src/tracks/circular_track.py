import math
import pygame
from tracks.track import Track
from core.car import Car

class CircularTrack(Track):
    def __init__(self, width, height):

        self.type = "procedural"

        
        self.spawn_position = (width // 2, height // 2 - 160)
        self.spawn_angle = 0  # ângulo inicial do carro

        self.car = Car(self.spawn_position[0],self.spawn_position[1]) # posição inicial do carro

        # Circle properties
        self.center = (width // 2, height // 2)  # Center of the screen
        self.radius = 200                    # Radius in pixels                             
        self.thickness = 80                     # 0 = filled circle     

        # Finish line properties
        inner_radius = self.radius - self.thickness

        self.finish_line_x = self.center[0]

        self.finish_line_y1 = self.center[1] - self.radius
        self.finish_line_y2 = self.center[1] - inner_radius 

        self.progress_state = {
            "total_progress": 0,
            "max_progress": 0,
            "last_angle": None
        }
        
                 

    def draw_track(self, surface):
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
    
    def reset_car(self, car):
        self.car = car
        self.car.x = self.spawn_position[0]
        self.car.y = self.spawn_position[1]
        self.car.speed = 0
        self.car.angle = self.spawn_angle

        self.last_position = (self.car.x, self.car.y)

    # ----------------------------
    # PROGRESS STATE
    # ----------------------------

    def reset_progress_state(self):
        return{
            "total_progress": 0,
            "max_progress": 0,
            "last_angle": None
        }

    def is_lap_complete(self, state):
        return state["total_progress"] >= 340

    def progress_logic(self, state, last_pos, current_pos):

        total_progress = state["total_progress"]
        last_angle = state["last_angle"]
        max_progress = state.get("max_progress", 0)

        current_angle = self.get_angle(*current_pos)

        # Primeira atualização (evita delta gigante)
        if last_angle is None:
            new_state = {
                "total_progress": 0,
                "max_progress": 0,
                "last_angle": current_angle
            }
            return new_state, False

        delta = current_angle - last_angle

        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        # aplica delta direto
        total_progress -= delta

        # trava limites
        total_progress = max(0, min(total_progress, 360))

        crossed = self.crossed_finish_line(last_pos, current_pos)

        # Atualiza max_progress
        if total_progress > max_progress:
            max_progress = total_progress
        else:
            # impede progresso passar do máximo alcançado
            total_progress = max_progress

        new_state = {
            "total_progress": total_progress,
            "max_progress": max_progress,
            "last_angle": current_angle
        }

        return new_state, crossed
    
    def _draw_progress(self, screen, env):

        bar_width = 200
        bar_height = 20

        bar_x = screen.get_width() - bar_width - 20
        bar_y = 20

        # Moldura
        pygame.draw.rect(
            screen,
            "white",
            (bar_x, bar_y, bar_width, bar_height),
            2
        )

        # progresso atual
        progress = env.progress_state["total_progress"]

        progress_ratio = progress / 360
        fill_width = bar_width * progress_ratio

        pygame.draw.rect(
            screen,
            "green",
            (bar_x, bar_y, fill_width, bar_height)
        )