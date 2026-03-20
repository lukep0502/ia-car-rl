from tracks.oval_track import OvalTrack


class ComplexTrack(OvalTrack):
    def __init__(self, width, height):
        super().__init__(
            width,
            height,
            rx_range=(200, 320),
            ry_range=(90, 200),
            thickness_range=(35, 70),
            checkpoints=6,
        )
