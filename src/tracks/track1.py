import math
import os
import pygame
from tracks.track import Track
from core.car import Car

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "track1.jpg")


class Track1(Track):

    def __init__(self, width, height):

        self.type = "image-based"
        self.progress_target = 100

        self.image_path = IMAGE_PATH

        loaded_image = pygame.image.load(self.image_path)
        if pygame.display.get_surface() is not None:
            self.image = loaded_image.convert()
        else:
            self.image = loaded_image

        self.width, self.height = self.image.get_size()

        self.track_mask = pygame.mask.from_threshold(
            self.image,
            (255, 255, 255),
            (30, 30, 30),
        )

        self.finish_mask = pygame.mask.from_threshold(
            self.image,
            (255, 0, 0),
            (30, 30, 30),
        )

        self.spawn_position = (width // 2 - 110, height // 2 - 65)
        self.spawn_angle = 0
        self.center = (width // 2, height // 2)

        self.car = Car(self.spawn_position[0], self.spawn_position[1])

        start_line = (width // 2 - 90, height // 2 - 90), (width // 2 - 90, height // 2 - 20)
        self.start_line = (start_line[0], start_line[1])

        self.checkpoints = [
            ((655, 280), (655, 340)),
            ((450, 520), (450, 580)),
            ((79, 400), (138, 380)),
        ]

        self.progress_state = self.reset_progress_state()

    def get_angle(self, x, y):
        dx = x - self.center[0]
        dy = self.center[1] - y
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360

    def is_on_track(self, x, y):

        x = int(x)
        y = int(y)

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False

        if self.track_mask.get_at((x, y)):
            return False

        return True

    def line_intersection(self, p1, p2, p3, p4):

        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
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

    def reset_progress_state(self):
        return {
            "next_checkpoint": 0,
            "total_progress": 0.0,
            "max_progress": 0.0,
            "lap_ready": False,
        }

    def is_lap_complete(self, state):
        return state.get("lap_ready", False)

    def progress_logic(self, state, last_pos, current_pos):

        next_cp = state["next_checkpoint"]
        max_progress = state.get("max_progress", 0.0)
        checkpoint_hit = False
        lap_ready = False

        if next_cp < len(self.checkpoints):
            cp_start, cp_end = self.checkpoints[next_cp]
            if self.line_intersection(last_pos, current_pos, cp_start, cp_end):
                next_cp += 1
                checkpoint_hit = True

        crossed_finish = False

        if next_cp == len(self.checkpoints):
            start_a, start_b = self.start_line
            if self.line_intersection(last_pos, current_pos, start_a, start_b):
                crossed_finish = True
                lap_ready = True
                next_cp = 0

        total_progress = self._compute_progress(next_cp, current_pos) * 100.0
        if crossed_finish:
            max_progress = 100.0
            total_progress = 0.0
        else:
            max_progress = max(max_progress, total_progress)

        new_state = {
            "next_checkpoint": next_cp,
            "total_progress": total_progress,
            "max_progress": max_progress,
            "lap_ready": lap_ready,
        }

        return new_state, crossed_finish, checkpoint_hit

    def distance(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _compute_progress(self, next_cp, car_pos):
        total_segments = len(self.checkpoints) + 1
        segment_index, prev_mid, next_mid = self._get_segment_reference(next_cp)

        segment_progress = self._project_on_segment(prev_mid, next_mid, car_pos)
        progress = (segment_index + segment_progress) / total_segments

        return max(0.0, min(1.0, progress))

    def get_progress_features(self, car_pos, car_angle, progress_state):
        next_cp = progress_state.get("next_checkpoint", 0)
        progress = self._compute_progress(next_cp, car_pos)

        _, prev_mid, next_mid = self._get_segment_reference(next_cp)
        target_dx = next_mid[0] - prev_mid[0]
        target_dy = next_mid[1] - prev_mid[1]
        target_angle = math.degrees(math.atan2(-target_dy, target_dx)) % 360.0
        angle_to_target = self.normalize_angle_to_target(target_angle, car_angle)

        return progress, angle_to_target

    def _get_segment_reference(self, next_cp):
        total_checkpoints = len(self.checkpoints)
        segment_index = min(next_cp, total_checkpoints)

        if next_cp < total_checkpoints:
            next_line = self.checkpoints[next_cp]
            if next_cp == 0:
                prev_line = self.start_line
            else:
                prev_line = self.checkpoints[next_cp - 1]
        else:
            prev_line = self.checkpoints[-1]
            next_line = self.start_line

        prev_mid = self._line_midpoint(prev_line)
        next_mid = self._line_midpoint(next_line)

        return segment_index, prev_mid, next_mid

    def _line_midpoint(self, line):
        return (
            (line[0][0] + line[1][0]) / 2.0,
            (line[0][1] + line[1][1]) / 2.0,
        )

    def _project_on_segment(self, start, end, point):
        seg_x = end[0] - start[0]
        seg_y = end[1] - start[1]
        seg_len_sq = max(1e-6, seg_x * seg_x + seg_y * seg_y)

        car_x = point[0] - start[0]
        car_y = point[1] - start[1]
        projection = (car_x * seg_x + car_y * seg_y) / seg_len_sq

        return max(0.0, min(1.0, projection))

    def _draw_progress(self, screen, env):

        bar_width = 200
        bar_height = 20
        bar_x = screen.get_width() - bar_width - 20
        bar_y = 20

        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, "gray", (bar_x, bar_y, bar_width, bar_height), 2)

        progress_ratio = max(0.0, min(1.0, env.progress_state.get("total_progress", 0.0) / 100.0))
        fill_width = int(bar_width * progress_ratio)

        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (bar_x, bar_y, fill_width, bar_height),
        )

    def draw_debug(self, screen):

        pygame.draw.line(
            screen,
            "red",
            self.start_line[0],
            self.start_line[1],
            3,
        )

        for cp in self.checkpoints:
            pygame.draw.line(
                screen,
                "blue",
                cp[0],
                cp[1],
                2,
            )
