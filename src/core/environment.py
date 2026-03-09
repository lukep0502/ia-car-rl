import pygame
from tracks import track

from core.car import Car



class Environment:

    def __init__(self, width, height, track):


        self.track = track
        
        self.race_finished = False

        self.laps = 0
        self.max_laps = 3   

        self.car = self.track.car 

        self.total_progress = 0
        self.last_angle = self.track.get_angle(self.car.x, self.car.y)

        self.start_time = pygame.time.get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0
        self.progress_state = 0

        self.last_position = (self.car.x, self.car.y)

        if self.track.type == "procedural":
            self.progress_state = {
                "total_progress": 0,
                "last_angle": self.track.get_angle(self.car.x, self.car.y)
            }
        else:
            self.progress_state = {
                "next_checkpoint": 0
            }

        

    def reset(self):

        self.laps = 0
        self.race_finished = False

        self.last_position = (self.car.x, self.car.y)

        self.start_time = pygame.time.get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0

        self.track.reset_car(self.car)
        self.track.reset_progress_state()

        print("Corrida reiniciada!")

    def step(self, action):

        if self.race_finished:
            return

        # Timing
        current_time = pygame.time.get_ticks()
        self.total_time = (current_time - self.start_time) / 1000
        self.current_lap_time = (current_time - self.lap_start_time) / 1000

        # salva posição anterior
        self.last_position = (self.car.x, self.car.y)


        # Update car
        self.car.update(action)

        if self.check_collision():
            self.car.x, self.car.y = self.last_position
            self.car.speed *= -0.4  # quica um pouco

        current_position = (self.car.x, self.car.y)

        self.progress_state, crossed = self.track.progress_logic(
            self.progress_state,
            self.last_position,
            current_position
        )

        if crossed:
            if self.track.is_lap_complete(self.progress_state):
                self.laps += 1
                print(f"Lap {self.laps}")

                # Atualiza tempo atual antes de comparar
                self.current_lap_time = (
                    pygame.time.get_ticks() - self.lap_start_time
                ) / 1000

                if self.best_lap_time is None or self.current_lap_time < self.best_lap_time:
                    self.best_lap_time = self.current_lap_time
                    print(f"New best lap: {self.best_lap_time:.2f}s")

                self.progress_state = self.track.reset_progress_state()

                self.lap_start_time = pygame.time.get_ticks()

                if self.laps >= self.max_laps:
                    self.race_finished = True
            else:
                print("Crossed but lap not complete")                

        self.last_position = current_position

        
    def check_collision(self):
        for point in self.car.get_corners():
            if not self.track.is_on_track(point[0], point[1]):
                return True
        return False