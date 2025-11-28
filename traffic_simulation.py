"""
Traffic Intersection Simulation with Fuzzy Logic Control
"""
import pygame
import random
from typing import List, Tuple
from fuzzy_controller import TrafficLightController


class Car:
    """Represents a vehicle in the simulation"""
    
    WIDTH = 30
    HEIGHT = 20
    MIN_SPACING = 40
    STOP_LINE_OFFSET = 50
    MAX_SPEED = 2.5
    
    def __init__(self, lane: str, car_id: int, direction: str):
        self.lane = lane
        self.id = car_id
        self.direction = direction
        self.speed = 0
        self.waiting_time = 0
        self.passed_intersection = False
        self.color = self._random_color()
        self._set_initial_position()
    
    def _random_color(self) -> Tuple[int, int, int]:
        """Generate a random car color"""
        colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 255, 100), (255, 100, 255), (100, 255, 255),
            (200, 150, 100), (150, 200, 100), (200, 100, 150)
        ]
        return random.choice(colors)
    
    def _set_initial_position(self):
        """Set initial position based on lane and direction"""
        spawn_offset = random.randint(0, 300)
        
        if self.direction == 'horizontal':
            if self.lane == 'east':
                self.x = -100 - spawn_offset
                self.y = 340
                self.max_speed = self.MAX_SPEED
            else:  # west
                self.x = 1100 + spawn_offset
                self.y = 360
                self.max_speed = -self.MAX_SPEED
        else:  # vertical
            if self.lane == 'north':
                self.x = 460
                self.y = -100 - spawn_offset
                self.max_speed = self.MAX_SPEED
            else:  # south
                self.x = 490
                self.y = 800 + spawn_offset
                self.max_speed = -self.MAX_SPEED
    
    def get_stop_line_position(self) -> float:
        """Get the position where car should stop at red light"""
        if self.direction == 'horizontal':
            return 400 - self.STOP_LINE_OFFSET if self.max_speed > 0 else 550 + self.STOP_LINE_OFFSET
        else:
            return 300 - self.STOP_LINE_OFFSET if self.max_speed > 0 else 400 + self.STOP_LINE_OFFSET
    
    def is_too_close_to_car_ahead(self, cars: List['Car']) -> bool:
        """Check if car is too close to the car ahead"""
        for other in cars:
            if other.id == self.id or other.direction != self.direction:
                continue
            
            if self.direction == 'horizontal':
                same_lane = abs(other.y - self.y) < 10
                if self.max_speed > 0:
                    ahead = other.x > self.x and other.x - self.x < self.MIN_SPACING
                else:
                    ahead = other.x < self.x and self.x - other.x < self.MIN_SPACING
                if same_lane and ahead:
                    return True
            else:
                same_lane = abs(other.x - self.x) < 10
                if self.max_speed > 0:
                    ahead = other.y > self.y and other.y - self.y < self.MIN_SPACING
                else:
                    ahead = other.y < self.y and self.y - other.y < self.MIN_SPACING
                if same_lane and ahead:
                    return True
        return False
    
    def is_in_intersection(self) -> bool:
        """Check if car is in the intersection"""
        return 400 <= self.x <= 550 and 300 <= self.y <= 400
    
    def should_stop_for_light(self, light_state: str) -> bool:
        """Determine if car should stop based on traffic light"""
        if light_state == 'GREEN':
            return False
        
        stop_line = self.get_stop_line_position()
        
        if self.direction == 'horizontal':
            if self.max_speed > 0:
                return stop_line <= self.x <= 400
            else:
                return 550 <= self.x <= stop_line
        else:
            if self.max_speed > 0:
                return stop_line <= self.y <= 300
            else:
                return 400 <= self.y <= stop_line
    
    def update(self, light_state: str, cars: List['Car']):
        """Update car position and state"""
        if not self.passed_intersection and self.is_in_intersection():
            self.passed_intersection = True
        
        should_stop = (
            self.should_stop_for_light(light_state) or
            self.is_too_close_to_car_ahead(cars)
        )
        
        if should_stop:
            self.speed = 0
            if not self.passed_intersection:
                self.waiting_time += 0.1
        else:
            self.speed = self.max_speed
        
        if self.direction == 'horizontal':
            self.x += self.speed
        else:
            self.y += self.speed
    
    def is_off_screen(self) -> bool:
        """Check if car has left the simulation area"""
        buffer = 200
        if self.direction == 'horizontal':
            return self.x < -buffer or self.x > 1000 + buffer
        else:
            return self.y < -buffer or self.y > 700 + buffer
    
    def draw(self, screen: pygame.Surface):
        """Draw the car"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.WIDTH, self.HEIGHT))
        
        # Draw direction indicator
        indicator_color = (255, 255, 255)
        if self.direction == 'horizontal':
            if self.max_speed > 0:
                points = [(self.x + self.WIDTH, self.y + self.HEIGHT//2),
                         (self.x + self.WIDTH - 8, self.y + 5),
                         (self.x + self.WIDTH - 8, self.y + self.HEIGHT - 5)]
            else:
                points = [(self.x, self.y + self.HEIGHT//2),
                         (self.x + 8, self.y + 5),
                         (self.x + 8, self.y + self.HEIGHT - 5)]
        else:
            if self.max_speed > 0:
                points = [(self.x + self.WIDTH//2, self.y + self.HEIGHT),
                         (self.x + 5, self.y + self.HEIGHT - 8),
                         (self.x + self.WIDTH - 5, self.y + self.HEIGHT - 8)]
            else:
                points = [(self.x + self.WIDTH//2, self.y),
                         (self.x + 5, self.y + 8),
                         (self.x + self.WIDTH - 5, self.y + 8)]
        
        pygame.draw.polygon(screen, indicator_color, points)


class TrafficLight:
    """Visual representation of a traffic light"""
    
    def __init__(self, x: int, y: int, direction: str):
        self.x = x
        self.y = y
        self.direction = direction
        self.state = 'RED'
        self.time_remaining = 0
        self.is_vertical = direction == 'vertical'
    
    def update(self, state: str, time_remaining: float):
        """Update light state and timer"""
        self.state = state
        self.time_remaining = max(0, time_remaining)
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw traffic light with timer"""
        housing_color = (40, 40, 40)
        
        # Draw housing
        if self.is_vertical:
            pygame.draw.rect(screen, housing_color, (self.x - 25, self.y - 60, 50, 120))
        else:
            pygame.draw.rect(screen, housing_color, (self.x - 60, self.y - 25, 120, 50))
        
        # Draw lights
        light_states = ['RED', 'YELLOW', 'GREEN']
        light_colors = {'RED': (255, 0, 0), 'YELLOW': (255, 255, 0), 'GREEN': (0, 255, 0)}
        
        for i, light_state in enumerate(light_states):
            if self.is_vertical:
                light_x, light_y = self.x, self.y - 40 + i * 40
            else:
                light_x, light_y = self.x - 40 + i * 40, self.y
            
            color = light_colors[light_state] if self.state == light_state else (80, 80, 80)
            pygame.draw.circle(screen, color, (light_x, light_y), 12)
            pygame.draw.circle(screen, (30, 30, 30), (light_x, light_y), 12, 2)
        
        # Draw timer
        timer_text = font.render(f"{self.time_remaining:.1f}s", True, (255, 255, 255))
        if self.is_vertical:
            timer_rect = timer_text.get_rect(center=(self.x, self.y + 50))
        else:
            timer_rect = timer_text.get_rect(center=(self.x, self.y + 30))
        screen.blit(timer_text, timer_rect)


class TrafficSimulation:
    """Main traffic intersection simulation"""
    
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fuzzy Logic Traffic Control Simulation")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.timer_font = pygame.font.Font(None, 28)
        self.info_font = pygame.font.Font(None, 36)
        
        # Controllers
        self.controller_h = TrafficLightController('horizontal')
        self.controller_v = TrafficLightController('vertical')
        
        # Traffic lights
        self.lights = {
            'horizontal': TrafficLight(800, 150, 'horizontal'),
            'vertical': TrafficLight(150, 500, 'vertical')
        }
        
        # Simulation state
        self.cars: List[Car] = []
        self.next_car_id = 0
        self.light_state = {'horizontal': 'GREEN', 'vertical': 'RED'}
        self.light_timer = 0
        self.current_green_duration = 30
        self.yellow_duration = 4
        
        # Random traffic generation rates
        self.spawn_rates = {
            'horizontal': random.uniform(0.03, 0.12),
            'vertical': random.uniform(0.03, 0.12)
        }
        self.last_spawn = {'horizontal': 0, 'vertical': 0}
        
        # Colors
        self.ROAD_COLOR = (60, 60, 60)
        self.LANE_MARKING = (200, 200, 200)
        self.INTERSECTION_COLOR = (80, 80, 80)
        self.BACKGROUND_COLOR = (20, 20, 30)
        
        print("=== Traffic Simulation Started ===")
        print(f"Horizontal spawn rate: {self.spawn_rates['horizontal']:.3f}")
        print(f"Vertical spawn rate: {self.spawn_rates['vertical']:.3f}")
    
    def generate_traffic(self):
        """Generate new cars with random rates"""
        current_time = pygame.time.get_ticks()
        
        for direction in ['horizontal', 'vertical']:
            time_since_last = current_time - self.last_spawn[direction]
            
            if random.random() < self.spawn_rates[direction] and time_since_last > 500:
                lane = random.choice(['east', 'west'] if direction == 'horizontal' else ['north', 'south'])
                new_car = Car(lane, self.next_car_id, direction)
                
                if not self._is_spawn_blocked(new_car):
                    self.cars.append(new_car)
                    self.next_car_id += 1
                    self.last_spawn[direction] = current_time
    
    def _is_spawn_blocked(self, new_car: Car) -> bool:
        """Check if spawn position is blocked"""
        for car in self.cars:
            if car.direction != new_car.direction:
                continue
            
            distance = abs(car.x - new_car.x) if new_car.direction == 'horizontal' else abs(car.y - new_car.y)
            if distance < Car.MIN_SPACING * 2:
                return True
        return False
    
    def update_lights(self):
        """Update traffic light states with fuzzy logic"""
        self.light_timer += 0.1
        
        # Update light displays
        for direction in ['horizontal', 'vertical']:
            time_remaining = 0
            if self.light_state[direction] == 'GREEN':
                time_remaining = self.current_green_duration - self.light_timer
            elif self.light_state[direction] == 'YELLOW':
                time_remaining = self.yellow_duration - self.light_timer
            
            self.lights[direction].update(self.light_state[direction], max(0, time_remaining))
        
        # State transitions
        if self.light_state['horizontal'] == 'GREEN' and self.light_timer >= self.current_green_duration:
            self.light_state['horizontal'] = 'YELLOW'
            self.light_timer = 0
        
        elif self.light_state['horizontal'] == 'YELLOW' and self.light_timer >= self.yellow_duration:
            self.light_state['horizontal'] = 'RED'
            self.light_state['vertical'] = 'GREEN'
            self.light_timer = 0
            self._calculate_green_time('vertical')
        
        elif self.light_state['vertical'] == 'GREEN' and self.light_timer >= self.current_green_duration:
            self.light_state['vertical'] = 'YELLOW'
            self.light_timer = 0
        
        elif self.light_state['vertical'] == 'YELLOW' and self.light_timer >= self.yellow_duration:
            self.light_state['vertical'] = 'RED'
            self.light_state['horizontal'] = 'GREEN'
            self.light_timer = 0
            self._calculate_green_time('horizontal')
    
    def _calculate_green_time(self, direction: str):
        """Calculate optimal green time using fuzzy logic"""
        direction_cars = [c for c in self.cars if c.direction == direction and not c.passed_intersection]
        
        if direction_cars:
            density = min(100, len(direction_cars) * 10)
            avg_wait = sum(c.waiting_time for c in direction_cars) / len(direction_cars)
            
            controller = self.controller_h if direction == 'horizontal' else self.controller_v
            self.current_green_duration = controller.compute_green_time(density, avg_wait)
            
            print(f"{direction.upper()}: Cars={len(direction_cars)}, Density={density:.1f}%, "
                  f"Wait={avg_wait:.1f}s → Green={self.current_green_duration:.1f}s")
        else:
            self.current_green_duration = 20
    
    def update_cars(self):
        """Update all car positions"""
        for car in self.cars[:]:
            car.update(self.light_state[car.direction], self.cars)
            
            if car.is_off_screen():
                self.cars.remove(car)
    
    def draw_roads(self):
        """Draw the intersection and roads"""
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Draw roads
        pygame.draw.rect(self.screen, self.ROAD_COLOR, (0, 300, self.width, 100))
        pygame.draw.rect(self.screen, self.ROAD_COLOR, (450, 0, 100, self.height))
        pygame.draw.rect(self.screen, self.INTERSECTION_COLOR, (400, 300, 150, 100))
        
        # Draw lane markings
        for i in range(0, self.width, 40):
            pygame.draw.rect(self.screen, self.LANE_MARKING, (i, 347, 20, 6))
        for i in range(0, self.height, 40):
            pygame.draw.rect(self.screen, self.LANE_MARKING, (497, i, 6, 20))
        
        # Draw stop lines
        pygame.draw.rect(self.screen, (255, 100, 100), (350, 300, 5, 100))
        pygame.draw.rect(self.screen, (255, 100, 100), (595, 300, 5, 100))
        pygame.draw.rect(self.screen, (255, 100, 100), (450, 250, 100, 5))
        pygame.draw.rect(self.screen, (255, 100, 100), (450, 445, 100, 5))
    
    def draw_ui(self):
        """Draw minimal UI with car counts"""
        h_cars = len([c for c in self.cars if c.direction == 'horizontal'])
        v_cars = len([c for c in self.cars if c.direction == 'vertical'])
        
        # Horizontal count (left side)
        h_text = self.info_font.render(f"H: {h_cars}", True, (255, 255, 100))
        self.screen.blit(h_text, (50, 340))
        
        # Vertical count (top)
        v_text = self.info_font.render(f"V: {v_cars}", True, (100, 255, 255))
        self.screen.blit(v_text, (470, 50))
    
    def run(self):
        """Main simulation loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Update simulation
            self.generate_traffic()
            self.update_lights()
            self.update_cars()
            
            # Draw everything
            self.draw_roads()
            for car in self.cars:
                car.draw(self.screen)
            for light in self.lights.values():
                light.draw(self.screen, self.timer_font)
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(10)
        
        pygame.quit()


if __name__ == "__main__":
    simulation = TrafficSimulation()
    simulation.run()