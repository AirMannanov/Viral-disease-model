from .simulation import Simulation
from .config import *
from .city import CityData
from typing import List
import pygame
import sys


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 102, 204)
YELLOW = (255, 255, 0)
CYANIC = (0, 255, 255)
GRAY = (200, 200, 200)


class TextBox:
    def __init__(self, x: int, y: int, w: int, h: int, text: str,
                 color=WHITE, text_color=BLACK,
                 border_color=BLACK, border_width: int=1, border_radius: int=10,
                 font: pygame.font.Font = None):
        self.rect = pygame.Rect(x, y, w, h)
        self.border_rect = pygame.Rect(x - border_width, y - border_width, w + 2 * border_width, h + 2 * border_width)
        self.color = color
        self.border_color = border_color
        self.text_color = text_color
        self.border_radius = border_radius
        font = pygame.font.Font(None, 36) if font is None else font
        self.text_surface = font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.border_color, self.border_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)
        screen.blit(self.text_surface, self.text_rect)


class Button(TextBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_clicked(self, event: pygame.event.Event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class SelectBox(TextBox):
    def __init__(self, *args, color_clicked=RED, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_clicked = color_clicked

    def is_clicked(self, event: pygame.event.Event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

    def press(self):
        self.color, self.color_clicked = self.color_clicked, self.color


class InputBox:
    def __init__(self, x: int, y: int , w: int, h: int,
                 text: str=None, base_text: str=None, defualt: str=None,
                 color=WHITE, text_color=BLACK,
                 border_color=BLACK, border_width: int=1, border_radius: int=10,
                 font: pygame.font.Font = None):
        self.rect = pygame.Rect(x, y, w, h)
        self.border_rect = pygame.Rect(x - border_width, y - border_width, w + 2 * border_width, h + 2 * border_width)
        self.color = color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.text = '' if text is None else text
        self.base_text = 'Ввод число: ' if base_text is None else base_text
        self.defualt = '0' if defualt is None else defualt
        self.error_message = ''
        self.font = pygame.font.Font(None, 36) if font is None else font
        self.active = False

    def is_clicked(self, event: pygame.event.Event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.border_color, self.border_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)

        if self.error_message:
            error_surface = self.font.render(self.error_message, True, RED)
            screen.blit(error_surface, error_surface.get_rect(center=self.rect.center))
        else:
            if self.text == '':
                text_surface = self.font.render(self.base_text + self.defualt, True, self.text_color)
            else:
                text_surface = self.font.render(self.base_text + self.text, True, self.text_color)
            screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def get_data(self) -> str:
        return self.defualt if self.text == '' else self.text

class Visualizer:
    WIDTH, HEIGHT = 1200, 700
    RATE_WIDTH_PANEL = 0.3
    RATE_WIDTH_MAP = 1 - RATE_WIDTH_PANEL
    WHITE = (255, 255, 255)
    WIDTH_PANEL = int(RATE_WIDTH_PANEL * WIDTH)
    WIDTH_MAP = WIDTH - WIDTH_PANEL
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

    def __init__(self) -> None:
        pygame.init()

        self.fonts = {
            'big': pygame.font.Font(None, 54),
            'medium': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }

        self.simulation_running = False
        self.radius_cities = {}
        self.starting_infection = {}
        self.cities_type = []
        self.selected_city_index: int = None
        self.clicked_inputbox: InputBox = None
        self.clicked_selectbox: SelectBox = None
        self.cities_selectboxes: List[SelectBox] = []
        self.cities_data: List[CityData] = []


        padding = int(self.WIDTH_PANEL * 0.04)
        button_width = int(self.WIDTH_PANEL * 0.44)
        button_y_offset = 550

        start_button_coords = (int(self.WIDTH * 0.35) + padding, int(self.HEIGHT * 0.825), int(self.WIDTH * 0.6) - padding, int(self.HEIGHT * 0.13))
        prev_button_coords = (self.WIDTH_MAP + padding, button_y_offset, button_width, 50)
        next_button_coords = (self.WIDTH_MAP + button_width + 2 * padding, button_y_offset, button_width, 50)
        exit_button_coords = (self.WIDTH_MAP + padding, button_y_offset + 50 + padding, button_width * 2 + padding , 50)
        spend_budger_inputbox_coords = (self.WIDTH_MAP + padding, button_y_offset - 50 - padding, button_width * 2 + padding , 50)
        textbox_coords = (self.WIDTH_MAP + padding, button_y_offset - 2 * (50 + padding), button_width * 2 + padding , 50)

        self.start_button = Button(*start_button_coords, "Начать симуляцию", color=RED, text_color=WHITE, font=self.fonts['big'])
        self.prev_button = Button(*prev_button_coords, "Предыдущий шаг", font=self.fonts['small'])
        self.next_button = Button(*next_button_coords, "Следующий шаг", font=self.fonts['small'])
        self.exit_button = Button(*exit_button_coords, "Установить новую конфигурацию", font=self.fonts['small'])
        self.textbox = TextBox(*textbox_coords, "Затраты на вакцины", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.spend_budget = InputBox(*spend_budger_inputbox_coords, text='0', font=self.fonts['small'])

        header_textbox_coords = (int(self.WIDTH * 0.03), int(self.HEIGHT * 0.03), int(self.WIDTH * 0.94), 60)

        x_textbox, y_textbox = int(self.WIDTH * 0.05), int(self.HEIGHT * 0.03) + padding + 60
        dx_textbox, dy_textbox = int(self.WIDTH * 0.3), 40

        x_inputbox = int(self.WIDTH * 0.06)
        dx_inputbox = int(self.WIDTH * 0.28)
        margin_inputbox = 12

        duration_textbox_coords = (x_textbox, y_textbox, dx_textbox, dy_textbox)
        duration_inputbox_coords = (x_inputbox, y_textbox + padding + dy_textbox, dx_inputbox, dy_textbox)

        y_textbox += 2 * (padding + dy_textbox) + margin_inputbox
        starting_month_textbox_coords  = (x_textbox, y_textbox, dx_textbox, dy_textbox)
        starting_month_inputbox_coords  = (x_inputbox, y_textbox + padding + dy_textbox, dx_inputbox, dy_textbox)

        y_textbox += 2 * (padding + dy_textbox) + margin_inputbox
        number_citis_textbox_coords = (x_textbox, y_textbox, dx_textbox, dy_textbox)
        number_citis_inputbox_coords = (x_inputbox, y_textbox + padding + dy_textbox, dx_inputbox, dy_textbox)

        y_textbox += 2 * (padding + dy_textbox) + margin_inputbox
        starting_budget_textbox_coords = (x_textbox, y_textbox, dx_textbox, dy_textbox)
        starting_budget_inputbox_coords = (x_inputbox, y_textbox + padding + dy_textbox, dx_inputbox, dy_textbox)

        y_textbox += 2 * (padding + dy_textbox) + margin_inputbox
        cost_vaccine_textbox_coords = (x_textbox, y_textbox, dx_textbox, dy_textbox)
        cost_vaccine_inputbox_coords = (x_inputbox, y_textbox + padding + dy_textbox, dx_inputbox, dy_textbox)

        self.header_textbox = TextBox(*header_textbox_coords, "Симуляция распространения вирусного заболевания", color=BLUE, text_color=WHITE, font=self.fonts['big'])

        self.duration_textbox = TextBox(*duration_textbox_coords, "Укажите длительность моделирования", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.duration_inputbox = InputBox(*duration_inputbox_coords, base_text="Введите кол-во месяцев: ", color=BLUE, defualt='1', text_color=WHITE, font=self.fonts['small'])

        self.starting_month_textbox = TextBox(*starting_month_textbox_coords, "Укажите начальный месяц", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.starting_month_inputbox = InputBox(*starting_month_inputbox_coords, base_text="Введите номер месяца: ", defualt='1', color=BLUE, text_color=WHITE, font=self.fonts['small'])

        self.number_citis_textbox = TextBox(*number_citis_textbox_coords, "Укажите количество городов", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.number_citis_inputbox = InputBox(*number_citis_inputbox_coords, color=BLUE, defualt='1', text_color=WHITE, font=self.fonts['small'])

        self.starting_budget_textbox = TextBox(*starting_budget_textbox_coords, "Укажите начальный бюджет", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.starting_budget_inputbox = InputBox(*starting_budget_inputbox_coords, color=BLUE, text_color=WHITE, font=self.fonts['small'])

        self.cost_vaccine_textbox = TextBox(*cost_vaccine_textbox_coords, "Укажите стоимость вакцины", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.cost_vaccine_inputbox = InputBox(*cost_vaccine_inputbox_coords, defualt='1', color=BLUE, text_color=WHITE, font=self.fonts['small'])

        x_div, y_div = int(self.WIDTH * 0.6) + 2 * padding, int(self.HEIGHT * 0.03) + padding + 60
        dx_div, dy_div = int(self.WIDTH * 0.35) - 2 * padding, 459
        self.div = TextBox(x_div, y_div, dx_div, dy_div, text='', color=GRAY)

        div_padding = 9
        x_div_elem, y_div_elem = x_div + div_padding, y_div + div_padding
        dx_div_elem, dy_div_elem = dx_div - 2 * div_padding, 36
        x_div_input, dx_div_input = x_div_elem + div_padding, dx_div_elem - 2 * div_padding

        div_type_textbox_coords = (x_div_elem, y_div_elem, dx_div_elem, dy_div_elem)
        div_type_inputbox_coords = (x_div_input, y_div_elem + div_padding + dy_div_elem, dx_div_input, dy_div_elem)

        y_div_elem += 2 * (dy_div_elem + div_padding)
        div_population_textbox_coords = (x_div_elem, y_div_elem, dx_div_elem, dy_div_elem)
        div_population_inputbox_coords = (x_div_input, y_div_elem + div_padding + dy_div_elem, dx_div_input, dy_div_elem)

        y_div_elem += 2 * (dy_div_elem + div_padding)
        div_infected_textbox_coords = (x_div_elem, y_div_elem, dx_div_elem, dy_div_elem)
        div_infected_inputbox_coords = (x_div_input, y_div_elem + div_padding + dy_div_elem, dx_div_input, dy_div_elem)

        y_div_elem += 2 * (dy_div_elem + div_padding)
        div_vaccinated_textbox_coords = (x_div_elem, y_div_elem, dx_div_elem, dy_div_elem)
        div_vaccinated_inputbox_coords = (x_div_input, y_div_elem + div_padding + dy_div_elem, dx_div_input, dy_div_elem)

        y_div_elem += 2 * (dy_div_elem + div_padding)
        div_transport_textbox_coords = (x_div_elem, y_div_elem, dx_div_elem, dy_div_elem)
        div_transport_inputbox_coords = (x_div_input, y_div_elem + div_padding + dy_div_elem, dx_div_input, dy_div_elem)

        self.div_type_textbox = TextBox(*div_type_textbox_coords, "Укажите тип города", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.div_type_inputbox = InputBox(*div_type_inputbox_coords, color=BLUE, text_color=WHITE, font=self.fonts['small'])

        self.div_population_textbox = TextBox(*div_population_textbox_coords, "Укажите население", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.div_population_inputbox = InputBox(*div_population_inputbox_coords, color=BLUE, text_color=WHITE, font=self.fonts['small'])

        self.div_infected_textbox = TextBox(*div_infected_textbox_coords, "Укажите количество заражённых", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.div_infected_inputbox = InputBox(*div_infected_inputbox_coords, color=BLUE, text_color=WHITE, font=self.fonts['small'])

        self.div_vaccinated_textbox = TextBox(*div_vaccinated_textbox_coords, "Укажите количество вакцинированных", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.div_vaccinated_inputbox = InputBox(*div_vaccinated_inputbox_coords, color=BLUE, text_color=WHITE, font=self.fonts['small'])

        self.div_transport_textbox = TextBox(*div_transport_textbox_coords, "Укажите уровнь транспорта", color=BLUE, text_color=WHITE, font=self.fonts['small'])
        self.div_transport_inputbox = InputBox(*div_transport_inputbox_coords, color=BLUE, text_color=WHITE, font=self.fonts['small'])

        for rate in self._RATE_CITIES_POINT:
            self._COORDINATES_POINTS.append((int(rate[0] * self.WIDTH_MAP), rate[1] * self.HEIGHT))

    def _set_cities_data(self) -> None:
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

    def _draw_cities(self) -> None:
        """Отрисовка городов на карте."""
        if self.current_step >= len(self.simulation.history):
            raise ValueError("step must be less than len(simulation.history)")
        cities = self.simulation.history[self.current_step]['cities']


        for index, city in enumerate(cities):
            x, y = self._COORDINATES_POINTS[index] # координаты города
            radius = self.radius_cities[city['name']] # радиус города

            infection_rate = city['number_infected'] / city['population']
            color = GREEN if infection_rate < 0.1 else YELLOW if infection_rate < 0.45 else RED
            color_border = CYANIC if self.starting_infection[city['name']] else BLACK
            pygame.draw.circle(self.screen, color_border, (x, y), radius)
            pygame.draw.circle(self.screen, color, (x, y), radius - 1)

            letter = "М" if self.cities_type[index] == "megapolis" else "Г" if self.cities_type[index] == "medium" else "П"
            letter_text = pygame.font.Font(None, int(radius * 1.5)).render(letter, True, BLACK)
            self.screen.blit(letter_text, (x - letter_text.get_width() // 2, y - letter_text.get_height() // 2))

            text = self.fonts['small'].render(city["name"], True, BLACK)
            x, y = x - text.get_width() // 2, y - radius - text.get_height() - 5
            pygame.draw.rect(self.screen, GRAY, (x - 2, y - 2, text.get_width() + 4, text.get_height() + 4), border_radius=1)
            pygame.draw.rect(self.screen, BLACK, (x - 3, y - 3, text.get_width() + 6, text.get_height() + 6), 1, 2)
            self.screen.blit(text, (x, y))

    def _draw_statistics(self) -> None:
        """Отрисовка статистики по городам."""
        if self.current_step >= len(self.simulation.history):
            raise ValueError("step must be less than len(simulation.history)")
        statistics = self.simulation.history[self.current_step]

        pygame.draw.rect(self.screen, GRAY, (self.WIDTH_MAP, 0, self.WIDTH_MAP, self.HEIGHT))
        pygame.draw.line(self.screen, BLACK, (self.WIDTH_MAP, 0), (self.WIDTH_MAP, self.HEIGHT))
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
            text = self.fonts['small'].render(stat, True, BLACK)
            x_offset = self.WIDTH_MAP + (self.WIDTH_PANEL - text.get_width()) // 2
            if i == 0:
                pygame.draw.rect(self.screen, BLACK, (x_offset - 5, y_offset - 5, text.get_width() + 10, text.get_height() + 10), width=1, border_radius=2)
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
                text = self.fonts['small'].render(stat, True, BLACK)
                x_offset = self.WIDTH_MAP + (self.WIDTH_PANEL - text.get_width()) // 2
                if i == 0:
                    pygame.draw.rect(self.screen, BLACK, (x_offset - 5, y_offset - 5, text.get_width() + 10, text.get_height() + 10), width=1, border_radius=2)
                self.screen.blit(text, (x_offset, y_offset))
                y_offset += 30

    def _draw_legend(self) -> None:
        """Отрисовка легенды."""
        legend_width = int(self.WIDTH_MAP * 0.15)
        legend_height = 100
        legend_x = self.WIDTH_MAP - legend_width - 20
        legend_y = self.HEIGHT - 115

        pygame.draw.rect(self.screen, GRAY, (legend_x, legend_y, legend_width, legend_height), border_radius=10)
        pygame.draw.rect(self.screen, BLACK, (legend_x, legend_y, legend_width, legend_height), 1, 10)

        legend_text = ["М - мегаполис", "Г - город", "П - посёлок"]
        y_offset = legend_y + 10
        for line in legend_text:
            text = self.fonts['small'].render(line, True, BLACK)
            self.screen.blit(text, (legend_x + 10, y_offset))
            y_offset += 30

    def _draw_month_week(self, month: int, week: int) -> None:
        """Отрисовка текущего месяца и недели."""
        rect_x, rect_y = 20, self.HEIGHT - 115
        rect_width, rect_height = int(self.WIDTH_MAP * 0.18), 100

        pygame.draw.rect(self.screen, GRAY, (rect_x, rect_y, rect_width, rect_height), border_radius=10)
        pygame.draw.rect(self.screen, BLACK, (rect_x, rect_y, rect_width, rect_height), 1, 10)

        month_text = self.fonts['small'].render(f"Месяц: {self.MONTHS[month % 12 - 1]}", True, BLACK)
        week_text = self.fonts['small'].render(f"Неделя: {week}", True, BLACK)

        self.screen.blit(month_text, (rect_x + 10, rect_y + 25))
        self.screen.blit(week_text, (rect_x + 10, rect_y + 62))

    def _draw_buttons_simulation(self) -> None:
        """Отображает кнопку для перехода к следующему шагу симуляции."""
        if self.current_step + 1 == len(self.simulation.history) and self.current_step < self.max_step:
            self.textbox.draw(self.screen)
            self.spend_budget.draw(self.screen)
        self.prev_button.draw(self.screen)
        self.next_button.draw(self.screen)
        self.exit_button.draw(self.screen)

    def _draw_setup_menu(self) -> None:

        self.header_textbox.draw(self.screen)
        self.start_button.draw(self.screen)

        self.duration_textbox.draw(self.screen)
        self.duration_inputbox.draw(self.screen)

        self.starting_month_textbox.draw(self.screen)
        self.starting_month_inputbox.draw(self.screen)

        self.number_citis_textbox.draw(self.screen)
        self.number_citis_inputbox.draw(self.screen)

        self.starting_budget_textbox.draw(self.screen)
        self.starting_budget_inputbox.draw(self.screen)

        self.cost_vaccine_textbox.draw(self.screen)
        self.cost_vaccine_inputbox.draw(self.screen)

        for selectbox in self.cities_selectboxes:
            selectbox.draw(self.screen)

        if self.clicked_selectbox is not None:
            city = self.cities_data[self.cities_selectboxes.index(self.clicked_selectbox)]
            self.div.draw(self.screen)

            self.div_type_textbox.draw(self.screen)
            if city['city_type'] == "megapolis":
                self.div_type_inputbox.defualt = 'мегаполис'
            elif city['city_type'] == "medium":
                self.div_type_inputbox.defualt = 'город'
            elif city['city_type'] == "town":
                self.div_type_inputbox.defualt = 'посёлок'
            else:
                raise AttributeError("Somthing went wrong.")
            self.div_type_inputbox.draw(self.screen)

            self.div_population_textbox.draw(self.screen)
            self.div_population_inputbox.defualt = str(city['population'])
            self.div_population_inputbox.draw(self.screen)

            self.div_infected_textbox.draw(self.screen)
            self.div_infected_inputbox.defualt = str(city['number_infected'])
            self.div_infected_inputbox.draw(self.screen)

            self.div_vaccinated_textbox.draw(self.screen)
            self.div_vaccinated_inputbox.defualt = str(city['number_vaccinated'])
            self.div_vaccinated_inputbox.draw(self.screen)

            self.div_transport_textbox.draw(self.screen)
            self.div_transport_inputbox.defualt = str(int(100 * city['transport']))
            self.div_transport_inputbox.draw(self.screen)

    def _handle_events_simulation(self) -> None:
        """Обработчик событий во время симуляции."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.spend_budget.error_message = ''
                self.spend_budget.active = False

                if (self.spend_budget.is_clicked(event) and
                    self.current_step + 1 == len(self.simulation.history) and
                    self.current_step < self.max_step):
                    self.spend_budget.active = True
                    self.spend_budget.text = ''

                elif self.prev_button.is_clicked(event):
                    self.current_step = max(0, self.current_step - 1)

                elif self.next_button.is_clicked(event):
                    if self.current_step < self.max_step:
                        if self.current_step + 1 == len(self.simulation.history):
                            money = int(self.spend_budget.text) if self.spend_budget.text != '' else 0
                            self.spend_budget.text = ''
                            self.simulation.make_step(money)
                        self.current_step += 1

                elif self.exit_button.is_clicked(event):
                    self.selected_city_index = None
                    self.simulation_running = False

                else:
                    for index, (_, radius) in enumerate(self.radius_cities.items()):
                        x, y = self._COORDINATES_POINTS[index]
                        distance = ((event.pos[0] - x) ** 2 + (event.pos[1] - y) ** 2) ** 0.5
                        if distance <= radius:
                            self.selected_city_index = index

            elif event.type == pygame.KEYDOWN and self.spend_budget.active and self.spend_budget.error_message == '':
                if event.key == pygame.K_RETURN:
                    self.spend_budget.active = False

                elif event.key == pygame.K_BACKSPACE:
                    self.spend_budget.text = self.spend_budget.text[:-1] if self.spend_budget.text != '' else ''

                else:
                    symbol: str = event.unicode
                    if symbol.isdigit():
                        self.spend_budget.text += symbol
                        money = int(self.spend_budget.text) if self.spend_budget.text != '' else 0
                        if self.simulation.government.budget < money:
                            self.spend_budget.error_message = "В доступе нет такой суммы денег!"
                            self.spend_budget.text = ''
                    else:
                        self.spend_budget.error_message = "Только цифры!"
                        self.spend_budget.text = ''

    def _check_input_symbol(self, symbol: str) -> None:
        if not isinstance(self.clicked_inputbox, InputBox):
            raise AttributeError("Somthing went wrong.")
        self.clicked_inputbox: InputBox

        if self.clicked_inputbox == self.duration_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                if not (1 <= int(self.clicked_inputbox.text) <= 120):
                    self.clicked_inputbox.error_message = "Число из диапазона [1, 120]"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.starting_month_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                if not (1 <= int(self.clicked_inputbox.text) <= 12):
                    self.clicked_inputbox.error_message = "Число из диапазона [1, 12]"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.number_citis_inputbox :
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                if not (1 <= int(self.clicked_inputbox.text) <= 10):
                    self.clicked_inputbox.error_message = "Число из диапазона [1, 10]"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''
            self._citites_list_control()

        elif self.clicked_inputbox == self.starting_budget_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                if not (0 <= int(self.clicked_inputbox.text) <= 1000000000000):
                    self.clicked_inputbox.error_message = "Число из диапазона [0, 10 ^ 12]"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.cost_vaccine_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                if not (1 <= int(self.clicked_inputbox.text) <= 10000000):
                    self.clicked_inputbox.error_message = "Число из диапазона [1, 10 ^ 6]"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.div_type_inputbox:
            if symbol.lower() == 'м':
                self.clicked_inputbox.text = 'мегаполис'
            elif symbol.lower() == 'г':
                self.clicked_inputbox.text = 'город'
            elif symbol.lower() == 'п':
                self.clicked_inputbox.text = 'посёлок'
            else:
                self.clicked_inputbox.error_message = "На выбор буквы: 'м', 'г', 'п'"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.div_population_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                if not (0 <= int(self.clicked_inputbox.text) <= 10000000000000):
                    self.clicked_inputbox.error_message = "Число из диапазона [0, 10 ^ 12]"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.div_infected_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                number = int(self.clicked_inputbox.text)
                vaccinated = int(self.div_vaccinated_inputbox.get_data())
                population = int(self.div_population_inputbox.get_data())

                if not (0 <= number <= 10000000000000):
                    self.clicked_inputbox.error_message = "Число из диапазона [0, 10 ^ 12]"
                    self.clicked_inputbox.text = ''
                if number + vaccinated > population:
                    self.clicked_inputbox.error_message = "Нельзя провосходить население!"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.div_vaccinated_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                number = int(self.clicked_inputbox.text)
                infected = int(self.div_infected_inputbox.get_data())
                population = int(self.div_population_inputbox.get_data())

                if not (0 <= number <= 10000000000000):
                    self.clicked_inputbox.error_message = "Число из диапазона [0, 10 ^ 12]"
                    self.clicked_inputbox.text = ''
                if number + infected > population:
                    self.clicked_inputbox.error_message = "Нельзя провосходить население!"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        elif self.clicked_inputbox == self.div_transport_inputbox:
            if symbol.isdigit():
                self.clicked_inputbox.text += symbol
                if not (0 <= int(self.clicked_inputbox.text) <= 100):
                    self.clicked_inputbox.error_message = "Число из диапазона [0, 100]"
                    self.clicked_inputbox.text = ''
            else:
                self.clicked_inputbox.error_message = "Только цифры!"
                self.clicked_inputbox.text = ''

        else:
            raise AttributeError("Somthing went wrong.")

    def _add_div_information(self) -> None:
        if self.clicked_selectbox is not None:
            city = self.cities_data[self.cities_selectboxes.index(self.clicked_selectbox)]

            if self.div_type_inputbox.get_data() == 'мегаполис':
                city['city_type'] = 'megapolis'
            elif self.div_type_inputbox.get_data() == 'город':
                city['city_type'] = 'medium'
            elif self.div_type_inputbox.get_data() == 'посёлок':
                city['city_type'] = 'town'
            else:
                raise AttributeError("Somthing went wrong.")
            city['population'] = int(self.div_population_inputbox.get_data())
            city['number_infected'] = int(self.div_infected_inputbox.get_data())
            city['number_vaccinated'] = int(self.div_vaccinated_inputbox.get_data())
            city['transport'] = float(self.div_transport_inputbox.get_data()) / 100

            self.div_type_inputbox.text = ''
            self.div_population_inputbox.text = ''
            self.div_infected_inputbox.text = ''
            self.div_vaccinated_inputbox.text = ''
            self.div_transport_inputbox.text = ''

    def _citites_list_control(self) -> None:
        number = int(self.number_citis_inputbox.get_data())
        self.clicked_selectbox = None
        del self.cities_selectboxes
        del self.cities_data
        self.cities_selectboxes: List[SelectBox] = []
        self.cities_data: List[CityData] = []

        padding = int(self.WIDTH_PANEL * 0.04)
        x_cities, y_cities = int(self.WIDTH * 0.35) + padding, int(self.HEIGHT * 0.03) + padding + 60
        dx_cities, dy_cities = int(self.WIDTH * 0.25), 45
        for index in range(1, number + 1):
            city_coords = (x_cities, y_cities, dx_cities, dy_cities)
            y_cities += dy_cities + 1
            self.cities_selectboxes.append(SelectBox(*city_coords, f"Город {index}", font=self.fonts['small'], color=BLUE, text_color=WHITE))
            self.cities_data.append(government_data['cities_data'][index - 1].copy())

    def _handle_events_setuping(self) -> None:
        """Обработчик событий во время конфигурации симуляции."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.clicked_inputbox is not None:
                    self.clicked_inputbox.error_message = ''
                    self.clicked_inputbox = None

                if self.duration_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.duration_inputbox

                elif self.starting_month_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.starting_month_inputbox

                elif self.number_citis_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.number_citis_inputbox

                elif self.starting_budget_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.starting_budget_inputbox

                elif self.cost_vaccine_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.cost_vaccine_inputbox

                elif self.div_type_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.div_type_inputbox

                elif self.div_population_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.div_population_inputbox

                elif self.div_infected_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.div_infected_inputbox

                elif self.div_vaccinated_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.div_vaccinated_inputbox

                elif self.div_transport_inputbox.is_clicked(event):
                    self.clicked_inputbox = self.div_transport_inputbox

                elif self.start_button.is_clicked(event):
                    self._add_div_information()
                    self._collect_data()
                    self.simulation_running = True
                    self._set_cities_data()

                else:
                    for selectbox in self.cities_selectboxes:
                        if selectbox.is_clicked(event):
                            self._add_div_information()
                            selectbox.press()
                            if self.clicked_selectbox is not None:
                                self.clicked_selectbox.press()
                            self.clicked_selectbox = selectbox
                            break

            elif event.type == pygame.KEYDOWN and self.clicked_inputbox is not None:
                if event.key == pygame.K_RETURN:
                    self.clicked_inputbox = None

                elif event.key == pygame.K_BACKSPACE and self.clicked_inputbox != self.div_type_inputbox:
                    self.clicked_inputbox.text = self.clicked_inputbox.text[:-1] if self.clicked_inputbox.text != '' else ''
                    if self.clicked_inputbox == self.number_citis_inputbox:
                        self._citites_list_control()

                else:
                    symbol: str = event.unicode
                    self._check_input_symbol(symbol)

    def _collect_data(self) -> None:
        simulation_data = {
            'months': int(self.duration_inputbox.get_data()),
            'start_month': int(self.starting_month_inputbox.get_data()),
            'government_data': {
                'name': 'Программляндия',
                'budget': int(self.starting_budget_inputbox.get_data()),
                'vaccine_cost': int(self.cost_vaccine_inputbox.get_data()),
                'cities_data': self.cities_data,
            }
        }
        self.simulation = Simulation(**simulation_data)
        self.current_step = 0
        self.max_step = self.simulation.months * 4

    def run_simulation(self):
        """Запустить симуляцию."""
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Моделирование распространения вируса")
        self.clock = pygame.time.Clock()
        self._citites_list_control()

        running = True
        while running:
            self.screen.fill(self.WHITE)

            if self.simulation_running:
                self._handle_events_simulation()

                month, week = self.simulation.start_month + self.current_step // 4, self.current_step % 4 + 1

                self._draw_cities()
                self._draw_legend()
                self._draw_month_week(month, week)
                self._draw_statistics()
                self._draw_buttons_simulation()

            else:
                self._handle_events_setuping()
                self._draw_setup_menu()


            pygame.display.flip()
            self.clock.tick(30)