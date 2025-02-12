from .simulation import Simulation
from .government import StatisticsData
import pygame
import sys

class Visualizer:
    WIDTH, HEIGHT = 1200, 700
    RATE_WIDTH_PANEL = 0.3
    RATE_WIDTH_MAP = 1 - RATE_WIDTH_PANEL
    WHITE = (255, 255, 255)
    WIDTH_PANEL = int(RATE_WIDTH_PANEL * WIDTH)
    WIDTH_MAP = WIDTH - WIDTH_PANEL
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    CYANIC = (0, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GRAY = (200, 200, 200)
    MAX_RADIUS = 50
    MIN_RADIUS = 20
    MONTHS = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    _RATE_CITIES_POINT = [
        (0.49, 0.52),
        (0.36, 0.27),
        (0.74, 0.42),
        (0.6, 0.15),
        (0.32, 0.76),
        (0.2, 0.5),
        (0.87, 0.2),
        (0.73, 0.7),
        (0.53, 0.9),
        (0.09, 0.13),
    ]
    _COORDINATES_POINTS = []


    def __init__(self, simulation: Simulation) -> None:
        pygame.init()

        self.simulation = simulation
        self.money = 0 # pass
        self.current_step = 0
        self.max_step = simulation.months * 4
        self.selected_city_index = None
        self.fonts = {
            'big': pygame.font.Font(None, 54),
            'medium': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }

        self.radius_cities = {}
        self.starting_infection = {}
        self.cities_type = []
        self._set_cities_date()

        self.button_color = (100, 100, 255)
        padding = int(self.WIDTH_PANEL * 0.04)
        button_width = int(self.WIDTH_PANEL * 0.44)
        button_y_offset = 550
        prev_button_coords = (self.WIDTH_MAP + padding, button_y_offset, button_width, 50)
        next_button_coords = (self.WIDTH_MAP + button_width + 2 * padding, button_y_offset, button_width, 50)
        exit_button_coords = (self.WIDTH_MAP + padding, button_y_offset + 50 + padding, button_width * 2 + padding , 50)

        self.prev_button = pygame.Rect(*prev_button_coords)
        self.next_button = pygame.Rect(*next_button_coords)
        self.exit_button = pygame.Rect(*exit_button_coords)

        for rate in self._RATE_CITIES_POINT:
            self._COORDINATES_POINTS.append((int(rate[0] * self.WIDTH_MAP), rate[1] * self.HEIGHT))


    def _set_cities_date(self) -> None:
        """Установка радиусов городов."""
        min_population, max_population = None, None
        for city in self.simulation.government.cities:
            min_population = min(min_population, city.population) if min_population is not None else city.population
            max_population = max(max_population, city.population) if max_population is not None else city.population
            self.starting_infection[city.name] = True if city.number_infected != 0 else False
            self.cities_type.append(city.city_type)

        if max_population != min_population:
            k = (self.MAX_RADIUS - self.MIN_RADIUS) / (max_population - min_population)
            c = self.MAX_RADIUS - k * max_population
        else:
            k = 0
            c = (self.MAX_RADIUS + self.MIN_RADIUS) // 2

        for city in self.simulation.government.cities:
            self.radius_cities[city.name] = k * city.population + c

    def draw_cities(self) -> None:
        """Отрисовка городов на карте."""
        if self.current_step >= len(self.simulation.history):
            raise ValueError("step must be less than len(simulation.history)")
        cities = self.simulation.history[self.current_step]['cities']


        for index, city in enumerate(cities):
            x, y = self._COORDINATES_POINTS[index] # координаты города
            radius = self.radius_cities[city['name']] # радиус города

            infection_rate = city['number_infected'] / city['population']
            color = self.GREEN if infection_rate < 0.1 else self.YELLOW if infection_rate < 0.45 else self.RED
            color_bored = self.CYANIC if self.starting_infection[city['name']] else self.BLACK
            pygame.draw.circle(self.screen, color_bored, (x, y), radius)
            pygame.draw.circle(self.screen, color, (x, y), radius - 1)

            letter = "М" if self.cities_type[index] == "megapolis" else "Г" if self.cities_type[index] == "medium" else "П"
            letter_text = pygame.font.Font(None, int(radius * 1.5)).render(letter, True, self.BLACK)
            self.screen.blit(letter_text, (x - letter_text.get_width() // 2, y - letter_text.get_height() // 2))

            text = self.fonts['small'].render(city["name"], True, self.BLACK)
            x, y = x - text.get_width() // 2, y - radius - text.get_height() - 5
            pygame.draw.rect(self.screen, self.GRAY, (x - 2, y - 2, text.get_width() + 4, text.get_height() + 4), border_radius=1)
            pygame.draw.rect(self.screen, self.BLACK, (x - 3, y - 3, text.get_width() + 6, text.get_height() + 6), 1, 2)
            self.screen.blit(text, (x, y))

    def draw_statistics(self) -> None:
        """Отрисовка статистики по городам."""
        if self.current_step >= len(self.simulation.history):
            raise ValueError("step must be less than len(simulation.history)")
        statistics = self.simulation.history[self.current_step]

        pygame.draw.rect(self.screen, self.GRAY, (self.WIDTH_MAP, 0, self.WIDTH_MAP, self.HEIGHT))
        pygame.draw.line(self.screen, self.BLACK, (self.WIDTH_MAP, 0), (self.WIDTH_MAP, self.HEIGHT))
        stats = [
            f"Данные по государству {statistics['government']['name']}",
            f"Больных: {statistics['government']['number_infected']}",
            f"Вакцинированных: {statistics['government']['number_vaccinated']}",
            f"Здоровых: {statistics['government']['population'] - statistics['government']['number_infected'] - statistics['government']['number_vaccinated']}",
            f"Бюджет государства: {statistics['government']['budget']}",
            f"Стоимость вакцины: {statistics['government']['vaccine_cost']}"
        ]
        y_offset = 20
        for i, stat in enumerate(stats):
            text = self.fonts['small'].render(stat, True, self.BLACK)
            x_offset = self.WIDTH_MAP + (self.WIDTH_PANEL - text.get_width()) // 2
            if i == 0:
                pygame.draw.rect(self.screen, self.BLACK, (x_offset - 5, y_offset - 5, text.get_width() + 10, text.get_height() + 10), width=1, border_radius=2)
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += 30

        if self.selected_city_index is not None:
            city = statistics['cities'][self.selected_city_index]
            city_stats = [
                f"Данные по городу {city['name']}",
                f"Больных: {city['number_infected']}",
                f"Вакцинированных: {city['number_vaccinated']}",
                f"Здоровых: {city['population'] - city['number_infected'] - city['number_vaccinated']}",
            ]
            y_offset += 10
            for i, stat in enumerate(city_stats):
                text = self.fonts['small'].render(stat, True, self.BLACK)
                x_offset = self.WIDTH_MAP + (self.WIDTH_PANEL - text.get_width()) // 2
                if i == 0:
                    pygame.draw.rect(self.screen, self.BLACK, (x_offset - 5, y_offset - 5, text.get_width() + 10, text.get_height() + 10), width=1, border_radius=2)
                self.screen.blit(text, (x_offset, y_offset))
                y_offset += 30

    def draw_legend(self) -> None:
        """Отрисовка легенды."""
        legend_width = int(self.WIDTH_MAP * 0.15)
        legend_height = 100
        legend_x = self.WIDTH_MAP - legend_width - 20
        legend_y = self.HEIGHT - 115

        pygame.draw.rect(self.screen, self.GRAY, (legend_x, legend_y, legend_width, legend_height), border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, (legend_x, legend_y, legend_width, legend_height), 1, 10)

        legend_text = ["М - мегаполис", "Г - город", "П - посёлок"]
        y_offset = legend_y + 10
        for line in legend_text:
            text = self.fonts['small'].render(line, True, self.BLACK)
            self.screen.blit(text, (legend_x + 10, y_offset))
            y_offset += 30

    def draw_month_week(self, month: int, week: int) -> None:
        """Отрисовка текущего месяца и недели."""
        rect_x, rect_y = 20, self.HEIGHT - 115
        rect_width, rect_height = int(self.WIDTH_MAP * 0.18), 100

        pygame.draw.rect(self.screen, self.GRAY, (rect_x, rect_y, rect_width, rect_height), border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, (rect_x, rect_y, rect_width, rect_height), 1, 10)

        month_text = self.fonts['small'].render(f"Месяц: {self.MONTHS[month - 1]}", True, self.BLACK)
        week_text = self.fonts['small'].render(f"Неделя: {week}", True, self.BLACK)

        self.screen.blit(month_text, (rect_x + 10, rect_y + 25))
        self.screen.blit(week_text, (rect_x + 10, rect_y + 62))

    def draw_buttons(self) -> None:
        """Отображает кнопку для перехода к следующему шагу симуляции."""
        pygame.draw.rect(self.screen, self.button_color, self.prev_button, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, self.prev_button, border_radius=10, width=1)
        text = self.fonts['small'].render("Предыдущий шаг", True, self.BLACK)
        text_rect = text.get_rect(center=self.prev_button.center)
        self.screen.blit(text, text_rect)

        pygame.draw.rect(self.screen, self.button_color, self.next_button, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, self.next_button, border_radius=10, width=1)
        text = self.fonts['small'].render("Следующий шаг", True, self.BLACK)
        text_rect = text.get_rect(center=self.next_button.center)
        self.screen.blit(text, text_rect)

        pygame.draw.rect(self.screen, self.button_color, self.exit_button, border_radius=10)
        pygame.draw.rect(self.screen, self.BLACK, self.exit_button, border_radius=10, width=1)
        text = self.fonts['small'].render("Установить новую конфигурацию", True, self.BLACK)
        text_rect = text.get_rect(center=self.exit_button.center)
        self.screen.blit(text, text_rect)

    def handle_next_button(self) -> None:
        """Обработка нажатия кнопки 'Следующий шаг'."""
        if self.current_step < self.max_step:
            if self.current_step < len(self.simulation.history):
                self.simulation.make_step(self.money)
            self.current_step += 1
        else:
            pass

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.prev_button.collidepoint(event.pos):
                    self.current_step = max(0, self.current_step - 1)
                elif self.next_button.collidepoint(event.pos):
                    self.handle_next_button()
                elif self.exit_button.collidepoint(event.pos):
                    pass
                else:
                    for index, (_, radius) in enumerate(self.radius_cities.items()):
                        x, y = self._COORDINATES_POINTS[index]
                        distance = ((event.pos[0] - x) ** 2 + (event.pos[1] - y) ** 2) ** 0.5
                        if distance <= radius:
                            self.selected_city_index = index

    def run(self):
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Моделирование распространения вируса")
        self.clock = pygame.time.Clock()

        running = True
        while running:
            self.handle_events()
            self.screen.fill(self.WHITE)
            self.draw_cities()
            self.draw_legend()
            month, week = self.simulation.start_month + self.current_step // 4, self.current_step % 4 + 1
            self.draw_month_week(month, week)
            self.draw_statistics()
            self.draw_buttons()

            pygame.display.flip()
            self.clock.tick(30)
