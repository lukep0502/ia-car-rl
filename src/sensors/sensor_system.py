import math
from sensors.raycast import RaySensor


class SensorSystem:

    def __init__(self):

        # ângulos dos sensores (em radianos)
        angles = [-60, -30, 0, 30, 60]

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

    def reset(self):
        self.last_points = []
