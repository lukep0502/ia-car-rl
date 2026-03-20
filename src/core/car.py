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

        # Aceleração
        if action["accelerate"]:
            self.speed += acceleration
        elif action["brake"]:
            self.speed -= acceleration
        else:
            # atrito natural
            if self.speed > 0:
                self.speed -= friction
            elif self.speed < 0:
                self.speed += friction

        # Limites de velocidade
        self.speed = max(self.max_reverse, min(self.speed, self.max_speed))

        # Direção só funciona se estiver em movimento
        if self.speed != 0:
            turn_speed = 2
            if action["left"]:
                self.angle += turn_speed
            if action["right"]:
                self.angle -= turn_speed

        # Movimento
        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y -= math.sin(rad) * self.speed


    def get_corners(self):

        length = 30
        width = 15

        rad = math.radians(self.angle)

        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        # Vetor frente
        front_dx = cos_a * length / 2
        front_dy = -sin_a * length / 2

        # Vetor lateral
        side_dx = sin_a * width / 2
        side_dy = cos_a * width / 2

        return [
            (self.x + front_dx + side_dx, self.y + front_dy + side_dy),
            (self.x + front_dx - side_dx, self.y + front_dy - side_dy),
            (self.x - front_dx + side_dx, self.y - front_dy + side_dy),
            (self.x - front_dx - side_dx, self.y - front_dy - side_dy),
        ]
    
