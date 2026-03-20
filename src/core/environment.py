import pygame
import time
from sensors.sensor_system import SensorSystem
from ai.reward import RewardSystem
from ai.normalization import normalize



class Environment:

    def __init__(self, width, height, track):


        self.track = track
        self._fallback_start = time.perf_counter()

        self.race_finished = False

        self.laps = 0
        self.max_laps = 3

        # Maximum allowed lap time (seconds) before the run is considered failed
        self.max_lap_time = 15
        self.lap_time_exceeded = False

        self.car = self.track.car 
        
        #ia
        self.reward_system = RewardSystem()
        self.sensor_system = SensorSystem()
        self.max_sensor_range = self.sensor_system.sensors[0].max_distance
        self.sensor_values = []
        self.sensor_points = []

        self.total_progress = 0
        self.last_angle = self.track.get_angle(self.car.x, self.car.y)

        self.start_time = self._get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0
        self.crossed = False
        self.lap_completed = False

        self.checkpoint_hit = False
        self.lap_time_exceeded = False
        self.progress_feature = 0.0
        self.prev_progress_feature = 0.0
        self.progress_delta_normalized = 0.0
        self.angle_to_target = 0.0
        self.good_steps = 0
        self.steps_without_progress = 0
        self.speed_normalized = 0.0

        # Debug/verbose mode (toggle during runtime)
        self.debug = False

        # Stuck detection (no movement/progress for a while)
        self.stuck = False
        self.stuck_counter = 0
        self.stuck_threshold = 45  # steps without progress before declaring stuck

        self.last_position = (self.car.x, self.car.y)

        if self.track.type == "procedural":
            self.progress_state = self.track.reset_progress_state()
        else:
            self.progress_state = self.track.reset_progress_state()

        

    def reset(self):

        self.laps = 0
        self.race_finished = False

        self.last_position = (self.car.x, self.car.y)

        self.start_time = self._get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0
        self.lap_time_exceeded = False
        self.collision = False
        self.stuck = False
        self.stuck_counter = 0
        self.lap_completed = False
        self.checkpoint_hit = False
        self.crossed = False
        self.progress_delta = 0
        self.progress_feature = 0.0
        self.prev_progress_feature = 0.0
        self.progress_delta_normalized = 0.0
        self.angle_to_target = 0.0
        self.good_steps = 0
        self.steps_without_progress = 0
        self.speed_normalized = 0.0

        # Per-episode stats (used for debugging overlays)
        self.current_episode = getattr(self, 'current_episode', 0)
        self.current_episode_reward = 0
        self.current_distance = 0

        # Reset reward internal state if available
        if hasattr(self.reward_system, "reset"):
            self.reward_system.reset()
        if hasattr(self.sensor_system, "reset"):
            self.sensor_system.reset()

        self.track.reset_car(self.car)
        self.progress_state = self.track.reset_progress_state()
        self.sensor_values, self.sensor_points = self.sensor_system.read(
            self.car,
            self.track
        )
        self._update_track_features((self.car.x, self.car.y))

        #print("Corrida reiniciada!")

    def step(self, action):

        if self.race_finished:
            return self.get_state(), 0, True

        # Timing
        current_time = self._get_ticks()
        self.total_time = (current_time - self.start_time) / 1000
        self.current_lap_time = (current_time - self.lap_start_time) / 1000

        # If lap takes too long, mark as failed and end the run
        if self.current_lap_time > self.max_lap_time:
            self.lap_time_exceeded = True
            self.race_finished = True
            if self.debug:
                print(f"Lap time exceeded: {self.current_lap_time:.1f}s (limit {self.max_lap_time}s)")

        # salva posição anterior
        self.last_position = (self.car.x, self.car.y)

        self.car.update(action)

        self.sensor_values, self.sensor_points = self.sensor_system.read(
                self.car,
                self.track
            )   
        self.speed_normalized = normalize(max(0.0, self.car.speed), self.car.max_speed)

        collision_happened = self.check_collision()
        self.collision = collision_happened

        current_position = (self.car.x, self.car.y)

        prev_checkpoint = self.progress_state.get("next_checkpoint")

        old_progress = self.progress_state.get("total_progress", 0)

        if self.collision:
            self.crossed = False
            self.checkpoint_hit = False
            progress_delta = 0
        else:
            self.progress_state, self.crossed, self.checkpoint_hit = self.track.progress_logic(
                self.progress_state,
                self.last_position,
                current_position
            )
            new_progress = self.progress_state.get("total_progress", 0)
            progress_delta = new_progress - old_progress

        self.progress_delta = progress_delta
        self.lap_completed = False
        self.prev_progress_feature = self.progress_feature

        feature_position = self.last_position if self.collision else current_position
        self._update_track_features(feature_position)
        self.progress_delta_normalized = max(0.0, self.progress_feature - self.prev_progress_feature)

        moving_forward = self.car.speed > 0.15
        made_progress = self.progress_delta_normalized > 0.0005

        if made_progress:
            self.good_steps += 1
            self.steps_without_progress = 0
        else:
            self.good_steps = 0
            self.steps_without_progress += 1

        # Stuck detection: the car is not building forward motion for long enough.
        if not moving_forward and not made_progress:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.stuck = False

        if self.stuck_counter >= self.stuck_threshold:
            self.stuck = True
            self.race_finished = True
            if self.debug:
                print(f"Stuck detected (no progress for {self.stuck_counter} steps)")

        if self.checkpoint_hit and self.debug:
            # Print the checkpoint that was just hit (before advancing)
            print(f"Checkpoint: {prev_checkpoint}")

        if self.crossed:
            if self.track.is_lap_complete(self.progress_state):
                self.lap_completed = True
                self.laps += 1

                # Atualiza tempo atual antes de comparar
                self.current_lap_time = (
                    self._get_ticks() - self.lap_start_time
                ) / 1000

                if self.best_lap_time is None or self.current_lap_time < self.best_lap_time:
                    self.best_lap_time = self.current_lap_time

                # Reset lap timer and progress sequencing for next lap
                self.lap_start_time = self._get_ticks()
                self.progress_state = self.track.reset_progress_state()

                # Check if race is finished
                if self.laps >= self.max_laps:
                    self.race_finished = True
                    if self.debug:
                        print(f"Race finished! Total laps: {self.laps}, Best lap: {self.best_lap_time:.2f}s")
                elif self.debug:
                    print(f"Lap {self.laps} completed! Time: {self.current_lap_time:.2f}s, Best: {self.best_lap_time:.2f}s")              

        self.last_position = current_position

        reward = self.reward_system.calculate(self)
        if self.stuck:
            reward -= 2.0

        done = False

        if self.collision:
            done = True

        if self.race_finished:
            done = True

        if self.lap_time_exceeded:
            done = True

        next_state = self.get_state()
        return next_state, reward, done

        
    def check_collision(self):

        for point in self.car.get_corners():

            x = int(point[0])
            y = int(point[1])

            if x < 0 or y < 0:
                return True

            if x >= self.track.width or y >= self.track.height:
                return True

            if not self.track.is_on_track(x, y):
                return True

        return False
    
    def get_state(self):
        if not self.sensor_values:
            self.sensor_values, self.sensor_points = self.sensor_system.read(
                self.car,
                self.track
            )

        progress, angle_to_target = self.track.get_progress_features(
            (self.car.x, self.car.y),
            self.car.angle,
            self.progress_state
        )
        self.progress_feature = max(0.0, min(1.0, progress))
        self.angle_to_target = max(-1.0, min(1.0, angle_to_target))

        left_sensor = self.sensor_values[1] if len(self.sensor_values) > 1 else self.max_sensor_range
        front_sensor = self.sensor_values[2] if len(self.sensor_values) > 2 else self.max_sensor_range
        right_sensor = self.sensor_values[3] if len(self.sensor_values) > 3 else self.max_sensor_range

        left = normalize(left_sensor, self.max_sensor_range)
        front = normalize(front_sensor, self.max_sensor_range)
        right = normalize(right_sensor, self.max_sensor_range)
        speed = normalize(max(0.0, self.car.speed), self.car.max_speed)
        self.speed_normalized = speed

        return [front, left, right, speed, self.progress_feature, self.angle_to_target]

    def _get_ticks(self):
        if pygame.get_init():
            return pygame.time.get_ticks()
        return int((time.perf_counter() - self._fallback_start) * 1000)

    def _update_track_features(self, car_pos):
        progress, angle_to_target = self.track.get_progress_features(
            car_pos,
            self.car.angle,
            self.progress_state
        )
        self.progress_feature = max(0.0, min(1.0, progress))
        self.angle_to_target = max(-1.0, min(1.0, angle_to_target))
