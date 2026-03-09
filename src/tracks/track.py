class Track:
    """
    Classe base para todos os tipos de pista.

    Cada pista deve implementar:
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
        Desenha a pista.
        Nem todas precisam implementar (ex: image track).
        """
        pass

    def draw_debug(self, surface):
        """
        Debug visual opcional.
        """
        pass

    # ---------------------------------
    # TRACK COLLISION
    # ---------------------------------

    def is_on_track(self, x, y):
        """
        Verifica se o carro está na pista.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} precisa implementar is_on_track()"
        )

    # ---------------------------------
    # PROGRESS SYSTEM
    # ---------------------------------

    def reset_progress_state(self):
        """
        Retorna estado inicial de progresso.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} precisa implementar reset_progress_state()"
        )

    def progress_logic(self, state, last_pos, current_pos):
        """
        Atualiza progresso da volta.

        Retorna:
        new_state, crossed_finish
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} precisa implementar progress_logic()"
        )

    def is_lap_complete(self, state):
        """
        Verifica se completou a volta.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} precisa implementar is_lap_complete()"
        )

    # ---------------------------------
    # CAR RESET
    # ---------------------------------

    def reset_car(self, car):
        """
        Reseta carro na posição inicial.
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
        UI de progresso (opcional).
        """
        pass