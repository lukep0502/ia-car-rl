import pygame
import math
from tracks.track import Track
from core.car import Car

IMAGE_PATH = "tracks/track1.jpg"

class Track1(Track):

    def __init__(self, width, height):

        self.type = "image-based"

        self.image_path = IMAGE_PATH

        self.image = pygame.image.load(self.image_path).convert()

        self.width, self.height = self.image.get_size()

        # máscara pista
        self.track_mask = pygame.mask.from_threshold(
            self.image,
            (255,255,255),
            (1,1,1)
        )

        # máscara linha chegada
        self.finish_mask = pygame.mask.from_threshold(
            self.image,
            (255,0,0),
            (1,1,1)
        )
        
        self.spawn_position = (width // 2 - 110, height // 2 - 65)
        self.spawn_angle = 0  # ângulo inicial do carro
        self.center = (width // 2, height // 2)

        self.car = Car(self.spawn_position[0],self.spawn_position[1]) # posição inicial do carro

        #checkpoints - start line
        start_line = (width // 2 - 90, height // 2 -90), (width // 2 - 90, height // 2 - 20)

        self.start_line = (start_line[0], start_line[1])

        self.checkpoints = [
            ((655,280),(655,340)),
            ((450,520),(450,580)),
            ((79,400),(138,380)),
        ]

        self.progress_state = self.reset_progress_state()
        
    def get_angle(self, x, y):
        dx = x - self.center[0]
        dy = self.center[1] - y  # invertido por causa do eixo do pygame
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360
    
    def is_on_track(self, x, y):

        x = int(x)
        y = int(y)

        # fora da imagem = fora da pista
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False

        # se tocar no branco → fora da pista
        if self.track_mask.get_at((x, y)):
            return False

        return True
    
    def line_intersection(self,p1, p2, p3, p4):

        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        # linhas paralelas
        if abs(denom) < 1e-9:
            return False

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom

        return 0 <= t <= 1 and 0 <= u <= 1

    
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

    # ===== RESET STATE =====
    def reset_progress_state(self):
        return {
            "next_checkpoint": 0
        }


    # ===== LAP CHECK =====
    def is_lap_complete(self, crossed_finish):
        return crossed_finish


   
    # ===== PROGRESS LOGIC =====
    def progress_logic(self, state, last_pos, current_pos):

        next_cp = state["next_checkpoint"]

        # ===== CHECKPOINT =====
        if next_cp < len(self.checkpoints):

            cp_start, cp_end = self.checkpoints[next_cp]

            if self.line_intersection(last_pos, current_pos, cp_start, cp_end):
                next_cp += 1
                print(f"Checkpoint {next_cp}/{len(self.checkpoints)}")

        # ===== FINISH LINE =====
        crossed_finish = False

        if next_cp == len(self.checkpoints):

            start_a, start_b = self.start_line

            if self.line_intersection(last_pos, current_pos, start_a, start_b):

                crossed_finish = True
                print("🏁 Finish line!")

                next_cp = 0

        new_state = {
            "next_checkpoint": next_cp
        }

        return new_state, crossed_finish
    
    def distance(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])
    
    def _draw_progress(self, screen, env):

        bar_width = 200
        bar_height = 20

        bar_x = screen.get_width() - bar_width - 20
        bar_y = 20

        pygame.draw.rect(screen, (40,40,40), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, "gray", (bar_x, bar_y, bar_width, bar_height), 2)

        checkpoints = env.track.checkpoints
        next_cp = env.progress_state["next_checkpoint"]
        total_segments = len(checkpoints) + 1   # inclui trecho final

        car_pos = (env.car.x, env.car.y)

        progress = next_cp

        # ---------- segmento atual ----------
        if next_cp < len(checkpoints):

            cp_start, cp_end = checkpoints[next_cp]
            cp_mid = ((cp_start[0]+cp_end[0])/2, (cp_start[1]+cp_end[1])/2)

            if next_cp == 0:
                prev = env.track.start_line
            else:
                prev = checkpoints[next_cp-1]

            prev_mid = ((prev[0][0]+prev[1][0])/2, (prev[0][1]+prev[1][1])/2)

        else:
            # último trecho → até a linha de chegada
            last_cp = checkpoints[-1]
            prev_mid = ((last_cp[0][0]+last_cp[1][0])/2,
                        (last_cp[0][1]+last_cp[1][1])/2)

            finish = env.track.start_line
            cp_mid = ((finish[0][0]+finish[1][0])/2,
                    (finish[0][1]+finish[1][1])/2)

        segment_len = self.distance(prev_mid, cp_mid)
        car_dist = self.distance(prev_mid, car_pos)

        segment_progress = min(car_dist / segment_len, 1)

        progress += segment_progress

        progress_ratio = progress / total_segments

        fill_width = int(bar_width * progress_ratio)

        pygame.draw.rect(
            screen,
            (0,200,0),
            (bar_x, bar_y, fill_width, bar_height)
        )

    def draw_debug(self, screen):

        # linha de chegada
        pygame.draw.line(
            screen,
            "red",
            self.start_line[0],
            self.start_line[1],
            3
        )

        # checkpoints
        for cp in self.checkpoints:
            pygame.draw.line(
                screen,
                "blue",
                cp[0],
                cp[1],
                2
            )
