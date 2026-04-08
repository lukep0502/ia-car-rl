class RewardSystem:

    def __init__(self):
        self.max_sensor_range = 200
        self.best_progress_feature = 0.0

    def reset(self):
        self.best_progress_feature = 0.0

    @staticmethod
    def _clamp(value, low=0.0, high=1.0):
        return max(low, min(high, value))

    def calculate(self, env):
        profile = getattr(env, "sensor_profile", {}) or {}

        front = self._clamp(profile.get("front", 1.0))
        left = self._clamp(profile.get("left", 1.0))
        right = self._clamp(profile.get("right", 1.0))
        left_wall = self._clamp(profile.get("left_wall", left))
        right_wall = self._clamp(profile.get("right_wall", right))
        balance = self._clamp(getattr(env, "corridor_balance", profile.get("balance", 0.0)), -1.0, 1.0)
        turn_hint = self._clamp(getattr(env, "sensor_turn_hint", profile.get("turn_hint", 0.0)), -1.0, 1.0)

        progress = self._clamp(getattr(env, "progress_delta_normalized", 0.0))
        progress_feature = self._clamp(getattr(env, "progress_feature", 0.0))
        new_best_progress = max(0.0, progress_feature - self.best_progress_feature)
        self.best_progress_feature = max(self.best_progress_feature, progress_feature)

        angle_to_target = self._clamp(getattr(env, "angle_to_target", 0.0), -1.0, 1.0)
        track_angle = self._clamp(
            getattr(env, "track_angle_to_target", angle_to_target),
            -1.0,
            1.0,
        )
        speed = self._clamp(getattr(env, "speed_normalized", 0.0))
        good_steps = getattr(env, "good_steps", 0)
        steps_without_progress = getattr(env, "steps_without_progress", 0)

        alignment = self._clamp(1.0 - (abs(angle_to_target) * 1.08))
        curve_need = self._clamp(
            max(
                abs(angle_to_target),
                abs(track_angle) * 0.92,
                abs(turn_hint) * 0.85,
            ) * 1.28
        )
        straight_factor = self._clamp(1.0 - (curve_need * 1.15))
        side_margin = min(left_wall, right_wall)
        safe_front = self._clamp((front - 0.12) / 0.88)
        front_danger = self._clamp((0.30 - front) / 0.30)
        side_danger = self._clamp((0.18 - side_margin) / 0.18)
        centering = self._clamp(1.0 - (abs(balance) * 1.45))

        target_speed_curve = max(0.24, 0.98 - (curve_need * 0.78))
        target_speed_front = max(0.18, min(1.0, (front - 0.08) / 0.92))
        target_speed_side = max(0.24, min(1.0, (side_margin - 0.05) / 0.80))
        target_speed = min(
            target_speed_curve,
            target_speed_front,
            target_speed_side + (straight_factor * 0.18),
        )
        overspeed = max(0.0, speed - target_speed)

        action = getattr(env, "last_action", {}) or {}
        steering_input = 0
        if bool(action.get("left")) and not bool(action.get("right")):
            steering_input = 1
        elif bool(action.get("right")) and not bool(action.get("left")):
            steering_input = -1

        desired_turn = 0
        if angle_to_target > 0.06:
            desired_turn = 1
        elif angle_to_target < -0.06:
            desired_turn = -1

        steering_match_bonus = 0.0
        steering_conflict_penalty = 0.0
        excess_steering_penalty = 0.0
        braking_control_bonus = 0.0

        if desired_turn and steering_input == desired_turn:
            steering_match_bonus = 0.28 + (curve_need * 0.92)
        elif desired_turn and steering_input == -desired_turn:
            steering_conflict_penalty = 0.45 + (curve_need * 0.95)
        elif not desired_turn and steering_input and speed > 0.35:
            excess_steering_penalty = 0.08 + (straight_factor * speed * 0.14)

        if (overspeed > 0.03 or front < 0.32) and bool(action.get("brake")):
            braking_control_bonus = min(
                1.1,
                0.22 + (overspeed * (2.2 + (curve_need * 1.2))),
            )

        progress_reward = progress * (92.0 + (curve_need * 24.0))
        best_progress_bonus = new_best_progress * 46.0
        consistency_bonus = min(good_steps * 0.05, 2.5)
        flow_reward = speed * alignment * safe_front * (
            1.1 + (straight_factor * 0.9) + (curve_need * 0.45)
        )
        straight_speed_bonus = speed * straight_factor * safe_front * 1.9
        corner_attack_bonus = min(speed, target_speed + 0.08) * curve_need * (
            0.7 + (safe_front * 1.1)
        )
        centering_bonus = centering * straight_factor * 0.35

        wall_penalty = ((1.0 - front) * 0.42) + ((1.0 - side_margin) * 0.18)
        danger_penalty = (
            front_danger * (0.9 + (speed * 5.8))
            + side_danger * (0.35 + (speed * 1.9))
        )
        overspeed_penalty = overspeed * (
            1.6 + (curve_need * 3.2) + (front_danger * 4.6)
        )
        no_progress_penalty = min(steps_without_progress * 0.022, 1.4)
        reverse_penalty = 0.55 if getattr(env, "car", None) and env.car.speed < -0.1 else 0.0
        stall_penalty = 0.18 if speed < 0.06 and progress <= 0.0005 else 0.0
        stuck_penalty = 7.0 if getattr(env, "stuck", False) else 0.0
        collision_penalty = 18.0 if getattr(env, "collision", False) else 0.0
        lap_timeout_penalty = 4.0 if getattr(env, "lap_time_exceeded", False) else 0.0

        checkpoint_bonus = 6.0 if getattr(env, "checkpoint_hit", False) else 0.0
        lap_bonus = 34.0 if getattr(env, "lap_completed", False) else 0.0

        reward = (
            progress_reward
            + best_progress_bonus
            + consistency_bonus
            + flow_reward
            + straight_speed_bonus
            + corner_attack_bonus
            + centering_bonus
            + steering_match_bonus
            + braking_control_bonus
            + checkpoint_bonus
            + lap_bonus
            - wall_penalty
            - danger_penalty
            - overspeed_penalty
            - no_progress_penalty
            - reverse_penalty
            - stall_penalty
            - stuck_penalty
            - collision_penalty
            - lap_timeout_penalty
            - steering_conflict_penalty
            - excess_steering_penalty
        )

        if progress <= 0.0005:
            reward -= 0.10

        return reward
