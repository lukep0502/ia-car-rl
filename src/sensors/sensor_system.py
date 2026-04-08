import math
from ai.normalization import normalize
from sensors.raycast import RaySensor


class SensorSystem:

    def __init__(self):

        # Positive offsets point to the car's left side. Keep a forward bias so
        # the agent can anticipate tighter corners without inflating the state.
        angles = [90, 55, 20, 0, -20, -55, -90]

        self.sensors = [
            RaySensor(math.radians(a))
            for a in angles
        ]

        self.last_points = []
        self.smoothing = 0.0


    def read(self, car, track):

        car_pos = (car.x, car.y)
        car_angle = car.angle

        readings = []
        points = []

        for i, sensor in enumerate(self.sensors):

            dist, point = sensor.cast(
                car_pos,
                car_angle,
                track
            )

            if point is None:
                point = car_pos

            # Optional smoothing for visualization only.
            if self.smoothing > 0 and len(self.last_points) > i:
                old = self.last_points[i]
                keep = self.smoothing
                blend = 1 - keep

                smooth_point = (
                    old[0] * keep + point[0] * blend,
                    old[1] * keep + point[1] * blend
                )
            else:
                smooth_point = point

            readings.append(dist)
            points.append(smooth_point)

        self.last_points = points

        return readings, points

    def build_profile(self, readings):
        if not readings:
            return {
                "front": 1.0,
                "left": 1.0,
                "right": 1.0,
                "left_wall": 1.0,
                "right_wall": 1.0,
                "left_arc": 1.0,
                "right_arc": 1.0,
                "balance": 0.0,
                "turn_hint": 0.0,
            }

        max_range = max(
            1,
            self.sensors[0].max_distance if self.sensors else 1
        )
        normalized = [normalize(value, max_range) for value in readings]

        if len(normalized) >= 7:
            left_far, left_mid, left_near, front, right_near, right_mid, right_far = normalized[:7]
        else:
            left_far = normalized[0] if len(normalized) > 0 else 1.0
            left_mid = normalized[1] if len(normalized) > 1 else left_far
            left_near = normalized[1] if len(normalized) > 1 else left_mid
            front = normalized[2] if len(normalized) > 2 else 1.0
            right_near = normalized[3] if len(normalized) > 3 else 1.0
            right_mid = normalized[3] if len(normalized) > 3 else right_near
            right_far = normalized[4] if len(normalized) > 4 else right_mid

        left_wall = min(left_near, (0.72 * left_mid) + (0.28 * left_far))
        right_wall = min(right_near, (0.72 * right_mid) + (0.28 * right_far))
        left_arc = min(1.0, (0.50 * left_near) + (0.32 * left_mid) + (0.18 * left_far))
        right_arc = min(1.0, (0.50 * right_near) + (0.32 * right_mid) + (0.18 * right_far))
        front_blend = min(1.0, (0.74 * front) + (0.13 * left_near) + (0.13 * right_near))
        corridor_balance = max(-1.0, min(1.0, left_wall - right_wall))
        turn_hint = max(-1.0, min(1.0, (left_arc - right_arc) * 1.35))

        return {
            "front": front_blend,
            "left": min(1.0, (0.65 * left_wall) + (0.35 * left_arc)),
            "right": min(1.0, (0.65 * right_wall) + (0.35 * right_arc)),
            "left_wall": left_wall,
            "right_wall": right_wall,
            "left_arc": left_arc,
            "right_arc": right_arc,
            "balance": corridor_balance,
            "turn_hint": turn_hint,
        }

    def reset(self):
        self.last_points = []
