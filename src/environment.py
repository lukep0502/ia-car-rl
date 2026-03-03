import pygame
import math

# pygame setup
WIDTH, HEIGHT = 800, 600
FPS = 60

class Track:
    def __init__(self):
        # Circle properties
        self.center = (WIDTH // 2, HEIGHT // 2)  # Center of the screen
        self.radius = 200                    # Radius in pixels                             
        self.thickness = 60                     # 0 = filled circle     

        # Finish line properties
        inner_radius = self.radius - self.thickness

        self.finish_line_x = self.center[0]

        self.finish_line_y1 = self.center[1] - self.radius
        self.finish_line_y2 = self.center[1] - inner_radius          

    def draw(self, surface):
        # Draw the circular track
        pygame.draw.circle(surface, "white", self.center, self.radius, self.thickness)

        # Draw finish line
        pygame.draw.line(
                surface,
                "red",
                (self.finish_line_x, self.finish_line_y1),
                (self.finish_line_x, self.finish_line_y2),
                3
            )

    def is_on_track(self, x, y):
        dx = x - self.center[0]
        dy = y - self.center[1]
        distance = math.sqrt(dx**2 + dy**2)

        outer_limit = self.radius
        inner_limit = self.radius - self.thickness

        return inner_limit < distance < outer_limit
    
    # Get the angle from the center of the track to a given point (x, y)
    def get_angle(self, x, y):
        dx = x - self.center[0]
        dy = self.center[1] - y  # invertido por causa do eixo do pygame
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360

    def crossed_finish_line(self, last_pos, current_pos):
            lx, ly = last_pos
            cx, cy = current_pos

            # Verifica se cruzou eixo X da linha
            crossed = (lx < self.finish_line_x and cx >= self.finish_line_x)

            # E está dentro da altura da linha
            inside_height = (
                self.finish_line_y1 <= cy <= self.finish_line_y2
            )

            return crossed and inside_height

class Car:
    def __init__(self, x, y, track):
        self.x = x
        self.y = y
        self.track = track

        self.width = 20
        self.height = 40

        self.angle = -90  # começa apontando para cima
        self.velocity = 0
        self.max_speed = 5
        self.acceleration = 0.2
        self.friction = 0.05
        self.rotation_speed = 3

    def update(self, keys):
        # Aceleração
        if keys[pygame.K_w]:
            self.velocity += self.acceleration
        if keys[pygame.K_s]:
            self.velocity -= self.acceleration

        # Limitar velocidade
        if self.velocity > self.max_speed:
            self.velocity = self.max_speed
        if self.velocity < -self.max_speed:
            self.velocity = -self.max_speed

        # Rotação
        if keys[pygame.K_a]:
            self.angle += self.rotation_speed
        if keys[pygame.K_d]:
            self.angle -= self.rotation_speed

        # Aplicar atrito
        if self.velocity > 0:
            self.velocity -= self.friction
        elif self.velocity < 0:
            self.velocity += self.friction

        # Movimento baseado no ângulo
        radians = math.radians(self.angle)
        new_x = self.x + math.cos(radians) * self.velocity
        new_y = self.y - math.sin(radians) * self.velocity

        # Só atualiza se estiver na pista
        if self.track.is_on_track(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            self.velocity = 0

    def draw(self, surface):
        rect = pygame.Rect(0, 0, self.width, self.height)
        rect.center = (self.x, self.y)

        # Criar superfície para rotacionar
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, "blue", (0, 0, self.width, self.height))

        rotated = pygame.transform.rotate(car_surface, self.angle)
        new_rect = rotated.get_rect(center=rect.center)

        surface.blit(rotated, new_rect.topleft)

class Game:
    # Initialize the game environment
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Car AI - Circular Track")
        self.clock = pygame.time.Clock()

        self.track = Track()
        self.running = True
        self.race_finished = False

        #laps system
        self.laps = 0
        self.max_laps = 3
        self.font = pygame.font.SysFont(None, 36)

        self.last_position = pygame.mouse.get_pos()

        # Initialize the car at the starting position
        self.car = Car(WIDTH // 2, HEIGHT // 2 - 200, self.track)

        # Initialize progress tracking variables
        self.total_progress = 0
        self.last_angle = self.track.get_angle(self.car.x, self.car.y)

        # Timing variables
        self.start_time = pygame.time.get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0

    # Main game loop
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()

        pygame.quit()

    # Reset the game state to start a new race
    def reset(self):
        self.laps = 0
        self.race_finished = False

        # Resetar carro
        self.car.x = WIDTH // 2
        self.car.y = HEIGHT // 2 - 200
        self.car.velocity = 0
        self.car.angle = -90

        self.last_position = (self.car.x, self.car.y)

        # Reset progress tracking and timing
        self.start_time = pygame.time.get_ticks()
        self.lap_start_time = self.start_time
        self.current_lap_time = 0
        self.best_lap_time = None
        self.total_time = 0
        self.total_progress = 0
        self.laps = 0
        self.race_finished = False

        print("Corrida reiniciada!")

    # Update game state, including checking for lap completion
    def update(self):

        #if the race is finished, do not update the car's position or check for lap completion
        if self.race_finished:
            return

        # Update timing
        current_time = pygame.time.get_ticks()

        self.total_time = (current_time - self.start_time) / 1000
        self.current_lap_time = (current_time - self.lap_start_time) / 1000

        # Update the car's position based on user input
        keys = pygame.key.get_pressed()
        self.car.update(keys)

        current_angle = self.track.get_angle(self.car.x, self.car.y)
        delta = current_angle - self.last_angle

        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        # Só acumula se for horário
        if delta < 0:
            self.total_progress += abs(delta)

        self.last_angle = current_angle

        # Não deixa progresso negativo
        if self.total_progress < 0:
            self.total_progress = 0

        current_position = (self.car.x, self.car.y)

        if self.track.crossed_finish_line(self.last_position, current_position):

            if self.total_progress >= 360:
                self.laps += 1

                lap_time = self.current_lap_time

                if self.best_lap_time is None or lap_time < self.best_lap_time:
                    self.best_lap_time = lap_time

                print(f"Volta {self.laps} - {lap_time:.2f}s")

                self.lap_start_time = pygame.time.get_ticks()
                self.total_progress = 0

                if self.laps >= self.max_laps:
                    self.race_finished = True
            else:
                print("Cruzou linha mas não completou 360°")

        self.last_position = current_position


    # Handle user input and other events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_r:
                    self.reset()
    
    # Render the track and any other game elements
    def render(self):

        # Clear the screen
        self.screen.fill(('black'))
        self.track.draw(self.screen)

        # Display lap count
        lap_text = self.font.render(f"Voltas: {self.laps}/{self.max_laps}", True, "white")
        self.screen.blit(lap_text, (20, 20))

        # Draw the car
        self.car.draw(self.screen)

        # ----- PROGRESS BAR -----
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH - bar_width - 20
        bar_y = 20

        # Fundo
        pygame.draw.rect(self.screen, "white", (bar_x, bar_y, bar_width, bar_height), 2)

        # Preenchimento proporcional
        progress_ratio = self.total_progress / 360
        fill_width = bar_width * progress_ratio

        pygame.draw.rect(
            self.screen,
            "green",
            (bar_x, bar_y, fill_width, bar_height)
        )

        # Display lap times
        font = pygame.font.SysFont(None, 30)

        lap_text = font.render(f"Lap: {self.laps}/{self.max_laps}", True, "white")
        self.screen.blit(lap_text, (20, 20))

        time_text = font.render(f"Lap Time: {self.current_lap_time:.2f}s", True, "white")
        self.screen.blit(time_text, (20, 50))

        total_text = font.render(f"Total Time: {self.total_time:.2f}s", True, "white")
        self.screen.blit(total_text, (20, 80))

        if self.best_lap_time:
            best_text = font.render(f"Best: {self.best_lap_time:.2f}s", True, "yellow")
            self.screen.blit(best_text, (20, 110))

        # Draw overlay if the race is finished
        if self.race_finished:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            big_font = pygame.font.SysFont(None, 72)
            text1 = big_font.render("CORRIDA FINALIZADA", True, "white")
            text2 = self.font.render("Pressione R para reiniciar", True, "white")
            text3 = self.font.render("Pressione ESC para sair", True, "white")

            self.screen.blit(text1, text1.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
            self.screen.blit(text2, text2.get_rect(center=(WIDTH//2, HEIGHT//2 + 20)))
            self.screen.blit(text3, text3.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()