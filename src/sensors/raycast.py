import math


class RaySensor:

    def __init__(self, angle_offset, max_distance=200):
        self.angle_offset = angle_offset
        self.max_distance = max_distance

    def cast(self, car_pos, car_angle, track):

        x, y = car_pos

        # Convert degrees to radians
        angle = math.radians(car_angle) + self.angle_offset

        for i in range(1, self.max_distance):

            test_x = int(x + math.cos(angle) * i)
            # Pygame uses inverted Y axis. Keep ray direction consistent with car kinematics.
            test_y = int(y - math.sin(angle) * i)

            # Procedural track
            if track.type == "procedural":

                if not track.is_on_track(test_x, test_y):
                    return i, (test_x, test_y)

            # Mask-based track
            else:

                if test_x < 0 or test_y < 0:
                    return i, (test_x, test_y)

                if test_x >= track.width or test_y >= track.height:
                    return i, (test_x, test_y)

                if track.track_mask.get_at((test_x, test_y)) == 1:
                    return i, (test_x, test_y)

        return self.max_distance, (test_x, test_y)
