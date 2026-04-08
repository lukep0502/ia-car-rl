class Track:
    """
    Base class for all track types.

    Each track must implement:
    - is_on_track
    - progress_logic
    - reset_progress_state
    - is_lap_complete
    """

    def __init__(self):
        self.type = "base"

        self.spawn_position = (0, 0)
        self.spawn_angle = 0

        self.start_line = None
        self.checkpoints = []

    # ---------------------------------
    # DRAW
    # ---------------------------------

    def draw_track(self, surface):
        """
        Draws the track.
        Not all tracks need to implement it (e.g. image-based track).
        """
        pass

    def draw_debug(self, surface):
        """
        Optional visual debug.
        """
        pass

    # ---------------------------------
    # TRACK COLLISION
    # ---------------------------------

    def is_on_track(self, x, y):
        """
        Checks whether the car is on the track.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement is_on_track()"
        )

    # ---------------------------------
    # PROGRESS SYSTEM
    # ---------------------------------

    def reset_progress_state(self):
        """
        Returns the initial progress state.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement reset_progress_state()"
        )

    def progress_logic(self, state, last_pos, current_pos):
        """
        Updates lap progress.

        Returns:
        new_state, crossed_finish
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement progress_logic()"
        )

    def is_lap_complete(self, state):
        """
        Checks whether the lap is complete.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement is_lap_complete()"
        )

    def get_progress_features(self, car_pos, car_angle, progress_state):
        """
        Returns a unified representation of progress and alignment.

        progress: 0.0 -> 1.0
        angle_to_target: -1.0 -> 1.0
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_progress_features()"
        )

    # ---------------------------------
    # CAR RESET
    # ---------------------------------

    def reset_car(self, car):
        """
        Resets the car to the initial position.
        """
        car.x = self.spawn_position[0]
        car.y = self.spawn_position[1]
        car.speed = 0
        car.angle = self.spawn_angle

        return (car.x, car.y)

    # ---------------------------------
    # UI
    # ---------------------------------

    def draw_progress(self, screen, env):
        """
        Optional progress UI.
        """
        pass

    def normalize_angle_to_target(self, target_angle_deg, car_angle_deg):
        angle_diff = (target_angle_deg - car_angle_deg + 180.0) % 360.0 - 180.0
        return max(-1.0, min(1.0, angle_diff / 180.0))
