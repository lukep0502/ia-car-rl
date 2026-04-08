import math


class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.max_speed = 5
        self.max_reverse = -2

    def update(self, action):
        acceleration = 0.2
        friction = 0.05

        if action["accelerate"]:
            self.speed += acceleration
        elif action["brake"]:
            self.speed -= acceleration
        else:
            if self.speed > 0:
                self.speed -= friction
            elif self.speed < 0:
                self.speed += friction

        self.speed = max(self.max_reverse, min(self.speed, self.max_speed))

        steering = 0
        if action["left"] and not action["right"]:
            steering = 1
        elif action["right"] and not action["left"]:
            steering = -1

        speed_abs = abs(self.speed)

        # Tight corners should be reachable when speed is controlled, without
        # making high-speed steering excessively twitchy.
        if steering and speed_abs > 0.05:
            speed_ratio = min(1.0, speed_abs / max(0.1, self.max_speed))
            turn_speed = 1.3 + (1.9 * (1.0 - speed_ratio))

            if action["brake"]:
                turn_speed += 0.6
            elif action["accelerate"] and speed_ratio > 0.7:
                turn_speed -= 0.25

            turn_speed = max(1.1, turn_speed)
            self.angle += steering * turn_speed

            steering_drag = 0.012 + (0.02 * speed_ratio)
            if action["brake"]:
                steering_drag += 0.015

            self.speed *= max(0.90, 1.0 - steering_drag)

        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed

    def get_corners(self):

        length = 30
        width = 15

        rad = math.radians(self.angle)

        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        # Front vector
        front_dx = cos_a * length / 2
        front_dy = -sin_a * length / 2

        # Side vector
        side_dx = sin_a * width / 2
        side_dy = cos_a * width / 2

        return [
            (self.x + front_dx + side_dx, self.y + front_dy + side_dy),
            (self.x + front_dx - side_dx, self.y + front_dy - side_dy),
            (self.x - front_dx + side_dx, self.y - front_dy + side_dy),
            (self.x - front_dx - side_dx, self.y - front_dy - side_dy),
        ]
