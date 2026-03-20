import math
import random
import pygame
from tracks.track import Track
from core.car import Car


class OvalTrack(Track):
    def __init__(
        self,
        width,
        height,
        rx_range=(180, 300),
        ry_range=(110, 220),
        thickness_range=(40, 80),
        checkpoints=4,
    ):
        self.width = width
        self.height = height
        self.type = "procedural"
        self.progress_target = 360

        self.center = (width // 2, height // 2)
        self.outer_rx = random.randint(*rx_range)
        self.outer_ry = random.randint(*ry_range)
        self.thickness = random.randint(*thickness_range)
        self.inner_rx = max(40, self.outer_rx - self.thickness)
        self.inner_ry = max(40, self.outer_ry - self.thickness)

        spawn_x = self.center[0]
        spawn_y = int(self.center[1] - (self.outer_ry + self.inner_ry) / 2)
        self.spawn_position = (spawn_x, spawn_y)
        self.spawn_angle = 0
        self.car = Car(self.spawn_position[0], self.spawn_position[1])

        self.num_checkpoints = checkpoints
        self.checkpoints = []
        self.checkpoint_angles = []
        for i in range(self.num_checkpoints):
            angle = math.radians(i * (360 / self.num_checkpoints))
            x1 = self.center[0] + math.cos(angle) * self.outer_rx
            y1 = self.center[1] - math.sin(angle) * self.outer_ry
            x2 = self.center[0] + math.cos(angle) * self.inner_rx
            y2 = self.center[1] - math.sin(angle) * self.inner_ry
            self.checkpoints.append(((x1, y1), (x2, y2)))

            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            self.checkpoint_angles.append(self.get_angle(mx, my))

        self.finish_line_x = self.center[0]
        self.finish_line_y1 = self.center[1] - self.outer_ry
        self.finish_line_y2 = self.center[1] - self.inner_ry

        self.spawn_track_angle = self.get_angle(*self.spawn_position)
        start_checkpoint = self._find_closest_checkpoint_index(self.spawn_track_angle)
        if start_checkpoint != 0:
            self.checkpoints = (
                self.checkpoints[start_checkpoint:] + self.checkpoints[:start_checkpoint]
            )
            self.checkpoint_angles = (
                self.checkpoint_angles[start_checkpoint:] + self.checkpoint_angles[:start_checkpoint]
            )

    def draw_track(self, surface):
        outer_rect = pygame.Rect(
            self.center[0] - self.outer_rx,
            self.center[1] - self.outer_ry,
            self.outer_rx * 2,
            self.outer_ry * 2,
        )
        inner_rect = pygame.Rect(
            self.center[0] - self.inner_rx,
            self.center[1] - self.inner_ry,
            self.inner_rx * 2,
            self.inner_ry * 2,
        )
        pygame.draw.ellipse(surface, "white", outer_rect)
        pygame.draw.ellipse(surface, "black", inner_rect)
        pygame.draw.line(
            surface,
            "red",
            (self.finish_line_x, self.finish_line_y1),
            (self.finish_line_x, self.finish_line_y2),
            3,
        )

    def is_on_track(self, x, y):
        dx = x - self.center[0]
        dy = y - self.center[1]
        outer_eq = (dx * dx) / (self.outer_rx * self.outer_rx) + (dy * dy) / (self.outer_ry * self.outer_ry)
        inner_eq = (dx * dx) / (self.inner_rx * self.inner_rx) + (dy * dy) / (self.inner_ry * self.inner_ry)
        return outer_eq <= 1.0 and inner_eq >= 1.0

    def get_angle(self, x, y):
        dx = x - self.center[0]
        dy = self.center[1] - y
        nx = dx / max(1.0, self.outer_rx)
        ny = dy / max(1.0, self.outer_ry)
        angle = math.degrees(math.atan2(ny, nx))
        return angle % 360

    def crossed_finish_line(self, last_pos, current_pos):
        lx, _ = last_pos
        cx, cy = current_pos
        crossed = lx < self.finish_line_x and cx >= self.finish_line_x and cx > lx
        inside_height = self.finish_line_y1 <= cy <= self.finish_line_y2
        return crossed and inside_height

    def reset_car(self, car):
        self.car = car
        self.car.x = self.spawn_position[0]
        self.car.y = self.spawn_position[1]
        self.car.speed = 0
        self.car.angle = self.spawn_angle

    def _angle_passed(self, start, end, target, clockwise):
        start %= 360
        end %= 360
        target %= 360
        if clockwise:
            if start >= end:
                return end < target <= start
            return target > end or target <= start
        if end >= start:
            return start < target <= end
        return target > start or target <= end

    def _find_closest_checkpoint_index(self, angle):
        best_idx = 0
        best_diff = 360
        for i, cp_angle in enumerate(self.checkpoint_angles):
            diff = abs((angle - cp_angle + 180) % 360 - 180)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        return best_idx

    def check_checkpoint(self, last_angle, current_angle, state):
        cp_index = state["next_checkpoint"]
        angle_cursor = last_angle
        hit_count = 0
        while True:
            target = self.checkpoint_angles[cp_index]
            if not self._angle_passed(angle_cursor, current_angle, target, True):
                break
            hit_count += 1
            cp_index = (cp_index - 1) % self.num_checkpoints
            angle_cursor = target
            if hit_count > self.num_checkpoints:
                break

        if hit_count:
            state["next_checkpoint"] = cp_index
            state["checkpoints_passed"] = min(
                self.num_checkpoints,
                state.get("checkpoints_passed", 0) + hit_count,
            )
            return state, True
        return state, False

    def reset_progress_state(self):
        return {
            "total_progress": 0,
            "max_progress": 0,
            "last_angle": None,
            "next_checkpoint": (self.num_checkpoints - 1),
            "ignore_finish_line": True,
            "ignore_checkpoints": True,
            "checkpoints_passed": 0,
        }

    def is_lap_complete(self, state):
        return (
            state.get("total_progress", 0) >= 340
            and state.get("checkpoints_passed", 0) >= self.num_checkpoints
        )

    def progress_logic(self, state, last_pos, current_pos):
        total_progress = state["total_progress"]
        last_angle = state["last_angle"]
        max_progress = state.get("max_progress", 0)
        current_angle = self.get_angle(*current_pos)

        if last_angle is None:
            state["last_angle"] = current_angle
            return state, False, False

        delta = current_angle - last_angle
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        checkpoint_hit = False
        if delta < 0:
            state, checkpoint_hit = self.check_checkpoint(last_angle, current_angle, state)

        if state.get("ignore_checkpoints"):
            checkpoint_hit = False
            state["ignore_checkpoints"] = False

        total_progress -= delta
        total_progress = max(0, min(total_progress, 360))

        crossed = self.crossed_finish_line(last_pos, current_pos)
        if state.get("ignore_finish_line"):
            crossed = False
            state["ignore_finish_line"] = False

        if total_progress > max_progress:
            max_progress = total_progress

        new_state = {
            "total_progress": total_progress,
            "max_progress": max_progress,
            "last_angle": current_angle,
            "next_checkpoint": state["next_checkpoint"],
            "checkpoints_passed": state.get("checkpoints_passed", 0),
            "ignore_finish_line": state.get("ignore_finish_line", False),
            "ignore_checkpoints": state.get("ignore_checkpoints", False),
        }
        return new_state, crossed, checkpoint_hit

    def get_progress_features(self, car_pos, car_angle, progress_state):
        current_angle = self.get_angle(*car_pos)
        progress = ((self.spawn_track_angle - current_angle) % 360.0) / 360.0
        target_angle = (current_angle - 90.0) % 360.0
        angle_to_target = self.normalize_angle_to_target(target_angle, car_angle)

        return progress, angle_to_target

    def _draw_progress(self, screen, env):
        bar_width = 200
        bar_height = 20
        bar_x = screen.get_width() - bar_width - 20
        bar_y = 20
        pygame.draw.rect(screen, "white", (bar_x, bar_y, bar_width, bar_height), 2)
        ratio = env.progress_state.get("total_progress", 0) / 360
        pygame.draw.rect(screen, "green", (bar_x, bar_y, bar_width * ratio, bar_height))

    def draw_checkpoints(self, surface, state=None):
        for i, checkpoint in enumerate(self.checkpoints):
            (x1, y1), (x2, y2) = checkpoint
            color = "green" if state and i == state.get("next_checkpoint") else "yellow"
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 3)
