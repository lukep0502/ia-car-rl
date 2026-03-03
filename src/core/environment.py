import pygame
from tracks.circular_track import CircularTrack
from core.car import Car

WIDTH, HEIGHT = 800, 600


class Environment:

    def __init__(self):
        self.track = CircularTrack()

        self.race_finished = False

        self.laps = 0
        self.max_laps = 3   

        self.car = Car(WIDTH // 2, HEIGHT // 2 - 160)

        self.total_progress = 0
        self.last_angle = self.track.get_angle(self.car.x, self.car.y)

        self.start_time = pygame.time.get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0

        self.last_position = (self.car.x, self.car.y)

    def reset(self):

        self.laps = 0
        self.race_finished = False

        self.car.x = WIDTH // 2
        self.car.y = HEIGHT // 2 - 160
        self.car.speed = 0
        self.car.angle = 0

        self.last_position = (self.car.x, self.car.y)

        self.start_time = pygame.time.get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0
        self.total_progress = 0

        print("Corrida reiniciada!")

    def step(self, action):

        if self.race_finished:
            return

        # Timing
        current_time = pygame.time.get_ticks()
        self.total_time = (current_time - self.start_time) / 1000
        self.current_lap_time = (current_time - self.lap_start_time) / 1000

        # Update car
        self.car.update(action)

        if self.check_collision():
            self.car.speed = -1

        # ===== Progress Logic =====

        current_angle = self.track.get_angle(self.car.x, self.car.y)
        delta = current_angle - self.last_angle

        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        if delta < 0:
            self.total_progress += abs(delta)

        self.last_angle = current_angle

        if self.total_progress < 0:
            self.total_progress = 0

        current_position = (self.car.x, self.car.y)

        if self.track.crossed_finish_line(self.last_position, current_position):

            if self.total_progress >= 350:
                self.laps += 1

                lap_time = self.current_lap_time

                if self.best_lap_time is None or lap_time < self.best_lap_time:
                    self.best_lap_time = lap_time

                print(f"Volta {self.laps} - {lap_time:.2f}s")

                self.lap_start_time = pygame.time.get_ticks()
                self.total_progress = 0

                if self.laps >= self.max_laps:
                    self.race_finished = True
            else:
                print("Cruzou linha mas não completou 360°")

        self.last_position = current_position

    def check_collision(self):
        for point in self.car.get_corners():
            if not self.track.is_on_track(point[0], point[1]):
                return True
        return False