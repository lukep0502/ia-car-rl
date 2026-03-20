from ai.normalization import normalize


class RewardSystem:

    def __init__(self):
        self.last_angle = 0
        self.max_sensor_range = 200

    def reset(self):
        self.last_angle = 0

    def calculate(self, env):
        sensors = env.sensor_values if env.sensor_values else [self.max_sensor_range]
        max_range = max(1, self.max_sensor_range)
        left_sensor = sensors[1] if len(sensors) > 1 else max_range
        front_sensor = sensors[2] if len(sensors) > 2 else max_range
        right_sensor = sensors[3] if len(sensors) > 3 else max_range

        left = normalize(left_sensor, max_range)
        front = normalize(front_sensor, max_range)
        right = normalize(right_sensor, max_range)
        front_proximity = 1.0 - front
        safe_front = max(0.0, min(1.0, (front - 0.18) / 0.82))
        danger_front = max(0.0, (0.32 - front) / 0.32)

        progress = max(0.0, getattr(env, "progress_delta_normalized", 0.0))
        progress = min(progress, 1.0)
        angle_to_target = getattr(env, "angle_to_target", 0.0)
        speed = getattr(env, "speed_normalized", 0.0)
        good_steps = getattr(env, "good_steps", 0)
        steps_without_progress = getattr(env, "steps_without_progress", 0)
        alignment = max(0.0, 1.0 - abs(angle_to_target))

        progress_reward = progress * 72.0
        consistency_bonus = min(good_steps * 0.06, 3.0)
        alignment_reward = alignment * 1.5
        movement_reward = speed * alignment * safe_front * 2.4
        wall_penalty = front_proximity * 0.35
        danger_penalty = danger_front * (0.5 + speed * 3.5)
        no_progress_penalty = min(steps_without_progress * 0.02, 1.0)
        stuck_penalty = 6.0 if getattr(env, "stuck", False) else 0.0
        collision_penalty = 10.0 if getattr(env, "collision", False) else 0.0
        checkpoint_bonus = 4.0 if getattr(env, "checkpoint_hit", False) else 0.0
        lap_bonus = 20.0 if getattr(env, "lap_completed", False) else 0.0
        reverse_penalty = 0.4 if getattr(env, "car", None) and env.car.speed < -0.1 else 0.0

        reward = (
            progress_reward
            + consistency_bonus
            + alignment_reward
            + movement_reward
            + checkpoint_bonus
            + lap_bonus
            - wall_penalty
            - danger_penalty
            - no_progress_penalty
            - stuck_penalty
            - collision_penalty
            - reverse_penalty
        )

        if progress <= 0.0005:
            reward -= 0.10

        if speed < 0.05 and progress <= 0.0005:
            reward -= 0.25

        return reward
