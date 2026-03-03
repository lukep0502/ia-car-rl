class BaseTrack:
    def draw(self, surface):
        raise NotImplementedError
    
    def is_on_track(self, x, y):
        raise NotImplementedError
    
    def crossed_finish_line(self, last_pos, current_pos):
        raise NotImplementedError