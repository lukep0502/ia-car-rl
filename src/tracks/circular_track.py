import math
import random

import pygame

from core.car import Car
from tracks.track import Track


class CircularTrack(Track):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.type = "procedural"

        # Circle properties
        self.center = (width // 2, height // 2)  # Center of the screen
        self.radius = random.randint(150, 300)
        self.thickness = random.randint(40, 80)
        self.progress_target = 360

        spawn_radius = self.radius - (self.thickness / 2)
        self.spawn_position = (int(self.center[0]), int(self.center[1] - spawn_radius))
        self.spawn_angle = 0
        self.car = Car(self.spawn_position[0], self.spawn_position[1])

        # Checkpoints
        self.num_checkpoints = 4
        self.checkpoints = []
        self.checkpoint_angles = []

        for i in range(self.num_checkpoints):
            angle = math.radians(i * (360 / self.num_checkpoints))

            x1 = self.center[0] + math.cos(angle) * self.radius
            y1 = self.center[1] - math.sin(angle) * self.radius

            x2 = self.center[0] + math.cos(angle) * (self.radius - self.thickness)
            y2 = self.center[1] - math.sin(angle) * (self.radius - self.thickness)

            self.checkpoints.append(((x1, y1), (x2, y2)))

            # Precompute the angle of this checkpoint segment (midpoint angle)
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            self.checkpoint_angles.append(self.get_angle(mx, my))

        # Finish line properties
        inner_radius = self.radius - self.thickness

        self.finish_line_x = self.center[0]

        self.finish_line_y1 = self.center[1] - self.radius
        self.finish_line_y2 = self.center[1] - inner_radius

        # Rotate checkpoint ordering so checkpoint 0 matches spawn position.
        self.spawn_track_angle = self.get_angle(*self.spawn_position)
        start_checkpoint = self._find_closest_checkpoint_index(self.spawn_track_angle)

        if start_checkpoint != 0:
            self.checkpoints = (
                self.checkpoints[start_checkpoint:] + self.checkpoints[:start_checkpoint]
            )
            self.checkpoint_angles = (
                self.checkpoint_angles[start_checkpoint:] + self.checkpoint_angles[:start_checkpoint]
            )

        self.progress_state = {
            "total_progress": 0,
            "max_progress": 0,
            "last_angle": None,
            "next_checkpoint": 0,
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
            3,
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
        dy = self.center[1] - y  # Inverted because of the pygame axis
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360

    def crossed_finish_line(self, last_pos, current_pos):
        lx, ly = last_pos
        cx, cy = current_pos

        # Check whether it crossed the line X axis from left to right (clockwise direction)
        crossed = (lx < self.finish_line_x and cx >= self.finish_line_x and cx > lx)

        # And it is within the line height
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

    def line_intersection(self, a1, a2, b1, b2):

        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(a1, a2, b1) != ccw(a1, a2, b2)

    def _angle_passed(self, start, end, target, clockwise: bool):
        """Returns True if moving from start->end passes the target angle."""
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
        """Return the checkpoint index whose angle is closest to the given angle."""
        best_idx = 0
        best_diff = 360
        for i, cp_angle in enumerate(self.checkpoint_angles):
            # Circular angular difference
            diff = abs((angle - cp_angle + 180) % 360 - 180)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        return best_idx

    def check_checkpoint(self, last_angle, current_angle, state):
        cp_index = state["next_checkpoint"]
        angle_cursor = last_angle
        hit_count = 0

        # Circular track is trained in clockwise direction. Only validate
        # checkpoints in this direction to avoid reverse-lap exploits.
        while True:
            target_angle = self.checkpoint_angles[cp_index]
            if not self._angle_passed(angle_cursor, current_angle, target_angle, True):
                break

            hit_count += 1
            cp_index = (cp_index - 1) % self.num_checkpoints
            angle_cursor = target_angle

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

    # ----------------------------
    # PROGRESS STATE
    # ----------------------------

    def reset_progress_state(self):
        return {
            "total_progress": 0,
            "max_progress": 0,
            "last_angle": None,
            # Start expecting the checkpoint *behind* the spawn point, since the car begins on the spawn checkpoint.
            "next_checkpoint": (self.num_checkpoints - 1),
            # Prevent an immediate finish-line trigger right after a lap reset
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

        # First, initialize last_angle
        if last_angle is None:
            state["last_angle"] = current_angle
            return state, False, False

        # Calculate angular variation in the correct direction (wrap 0-360)
        delta = current_angle - last_angle

        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        # Forward on this layout is clockwise (negative delta).
        moving_forward = delta < 0

        # Only count checkpoints when moving forward to prevent direction exploits.
        checkpoint_hit = False
        if moving_forward:
            state, checkpoint_hit = self.check_checkpoint(last_angle, current_angle, state)

        # Ignore checkpoint hit immediately after a reset (so lap 2 doesn't start with checkpoint 0 instantly)
        if state.get("ignore_checkpoints"):
            checkpoint_hit = False
            state["ignore_checkpoints"] = False

        # Apply delta directly
        total_progress -= delta

        # Clamp limits
        total_progress = max(0, min(total_progress, 360))

        crossed = self.crossed_finish_line(last_pos, current_pos)

        # Ignore finish-line crossing immediately after a reset
        if state.get("ignore_finish_line"):
            crossed = False
            state["ignore_finish_line"] = False

        # Update max_progress
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

        # Border
        pygame.draw.rect(
            screen,
            "white",
            (bar_x, bar_y, bar_width, bar_height),
            2,
        )

        # Current progress
        progress = env.progress_state["total_progress"]

        progress_ratio = progress / 360
        fill_width = bar_width * progress_ratio

        pygame.draw.rect(
            screen,
            "green",
            (bar_x, bar_y, fill_width, bar_height),
        )

    def draw_checkpoints(self, surface, state=None):
        line_width = 3

        for i, checkpoint in enumerate(self.checkpoints):
            (x1, y1), (x2, y2) = checkpoint

            color = "yellow"

            if state and i == state["next_checkpoint"]:
                color = "green"

            pygame.draw.line(
                surface,
                color,
                (x1, y1),
                (x2, y2),
                line_width,
            )
