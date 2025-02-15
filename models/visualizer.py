from .simulation import Simulation
from .config import *
from .city import CityData
from typing import List, Dict
import pygame
import sys


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (236, 110, 86)
GREEN = (143, 208, 78)
BLUE = (45, 155, 240)
YELLOW = (252, 245, 68)
CYANIC = (0, 255, 255)
GRAY = (200, 200, 200)
ORANGE = (249, 199, 16)


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
        self.font = pygame.font.Font(None, 36) if font is None else font
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.border_color, self.border_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)
        screen.blit(self.text_surface, self.text_rect)

    def set_text(self, text: str):
        self.text_surface = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)


class Button(TextBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_clicked(self, event: pygame.event.Event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class SelectBox(Button):
    def __init__(self, *args, color_clicked=RED, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_clicked = color_clicked

    def press(self):
        self.color, self.color_clicked = self.color_clicked, self.color


class InputBox:
    def __init__(self, x: int, y: int , w: int, h: int,
                 text: str=None, base_text: str=None, default: str=None,
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
        self.default = '0' if default is None else default
        self.error_message = ''
        self.font = pygame.font.Font(None, 36) if font is None else font
        self.active = False

    def is_clicked(self, event: pygame.event.Event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.border_color, self.border_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)

        if self.error_message:
            if self.color != RED:
                error_surface = self.font.render(self.error_message, True, RED)
            else:
                error_surface = self.font.render(self.error_message, True, WHITE)
            screen.blit(error_surface, error_surface.get_rect(center=self.rect.center))
        else:
            if self.text == '':
                text_surface = self.font.render(self.base_text + self.default, True, self.text_color)
            else:
                text_surface = self.font.render(self.base_text + self.text, True, self.text_color)
            screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def get_data(self) -> str:
        return self.default if self.text == '' else self.text


class SelectBar:
    def __init__(self, x: int, y: int, w: int, h: int, options: List[str], default_selected: str=None,
                 background_color=WHITE, text_color=BLACK, box_color=WHITE, color_clicked=RED,
                 border_color=BLACK, border_width: int=1, border_radius: int=0,
                 box_border_color=BLACK, box_border_width: int=1, box_border_radius: int=10,
                 font: pygame.font.Font = None):
        height = h * len(options)
        self.rect = pygame.Rect(x, y, w, height)
        self.border_rect = pygame.Rect(x - border_width, y - border_width, w + 2 * border_width, height + 2 * border_width)
        self.color = background_color
        self.text_color = text_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.font = pygame.font.Font(None, 36) if font is None else font
        self.selectboxes: Dict[str, SelectBox] = {}
        self.selected = default_selected

        for i, option in enumerate(options):
            self.selectboxes[option] = SelectBox(
                                            x, y + i * h, w, h, option,
                                            color=box_color, color_clicked=color_clicked,
                                            border_color=box_border_color,
                                            border_width=box_border_width,
                                            border_radius=box_border_radius,
                                            font=self.font
                                        )

        if self.selected is not None:
            self.selectboxes[self.selected].press()

    def is_clicked(self, event: pygame.event.Event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.border_color, self.border_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.border_radius)
        for _, selectbox in self.selectboxes.items():
            selectbox.draw(screen)

    def click_option(self, event: pygame.event.Event):
        for option, selectbox in self.selectboxes.items():
            if selectbox.is_clicked(event) and self.selected != option:
                if self.selected is not None:
                    self.selectboxes[self.selected].press()
                selectbox.press()
                self.selected = option

    def choose(self, option: str):
        if option not in self.selectboxes:
            raise ValueError(f"No such option {option} in selectbar")
        if option != self.selected:
            if self.selected is not None:
                self.selectboxes[self.selected].press()
            self.selectboxes[option].press()
            self.selected = option

    def get_data(self):
        return self.selected


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
        self.radius_cities: Dict[str, float] = {}
        self.starting_infection: Dict[str, bool] = {}
        self.cities_type: List = []
        self.selected_city_index: int = None
        self.clicked_box: InputBox = None
        self.clicked_selectbox: SelectBox = None
        self.cities_selectboxes: List[SelectBox] = []
        self.cities_data: List[CityData] = []

        padding = int(self.WIDTH_PANEL * 0.04)
        button_width = int(self.WIDTH_PANEL * 0.44)
        button_y_offset = 550

        start_button_coords = (int(self.WIDTH * 0.35) + padding, int(self.HEIGHT * 0.825), int(self.WIDTH * 0.6) - padding, int(self.HEIGHT * 0.13))
        prev_button_coords = (self.WIDTH_MAP + padding, button_y_offset, button_width, 50)
        next_button_coords = (self.WIDTH_MAP + button_width + 2 * padding, button_y_offset, button_width, 50)
        config_button_coords = (self.WIDTH_MAP + padding, button_y_offset + 50 + padding, button_width * 2 + padding , 50)
        exit_button_coords = (5, 5, 20, 20)
        spend_budget_inputbox_coords = (self.WIDTH_MAP + padding, button_y_offset - 50 - padding, button_width * 2 + padding , 50)
        textbox_coords = (self.WIDTH_MAP + padding, button_y_offset - 2 * (50 + padding), button_width * 2 + padding , 50)

        self.start_button = Button(*start_button_coords, "Начать симуляцию", color=RED, font=self.fonts['big'])
        self.prev_button = Button(*prev_button_coords, "Предыдущий шаг", font=self.fonts['small'])
        self.next_button = Button(*next_button_coords, "Следующий шаг", font=self.fonts['small'])
        self.config_button = Button(*config_button_coords, "Установить новую конфигурацию", font=self.fonts['small'])
        self.exit_button = Button(*exit_button_coords, "x", color=RED, font=self.fonts['small'], border_radius=0)
        self.textbox = TextBox(*textbox_coords, "Укажите затраты на вакцины", color=ORANGE, font=self.fonts['small'])
        self.spend_budget_button = InputBox(*spend_budget_inputbox_coords, base_text="Число:  ", text='0', font=self.fonts['small'])


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

        self.header_textbox = TextBox(*header_textbox_coords, "Симуляция распространения вирусного заболевания", color=BLUE, font=self.fonts['big'])

        self.duration_textbox = TextBox(*duration_textbox_coords, "Укажите длительность моделирования", color=ORANGE, font=self.fonts['small'])
        self.duration_inputbox = InputBox(*duration_inputbox_coords, base_text="Число от 1 до 12:  ", color=RED, default='1', font=self.fonts['small'])

        self.starting_month_textbox = TextBox(*starting_month_textbox_coords, "Укажите начальный месяц", color=ORANGE, font=self.fonts['small'])
        self.starting_month_inputbox = InputBox(*starting_month_inputbox_coords, base_text="Число от 1 до 12:  ", default='1', color=RED, font=self.fonts['small'])

        self.number_citis_textbox = TextBox(*number_citis_textbox_coords, "Укажите количество городов", color=ORANGE, font=self.fonts['small'])
        self.number_citis_inputbox = InputBox(*number_citis_inputbox_coords, color=RED, base_text="Число от 1 до 10:  ", default='1', font=self.fonts['small'])

        self.starting_budget_textbox = TextBox(*starting_budget_textbox_coords, "Укажите начальный бюджет", color=ORANGE, font=self.fonts['small'])
        self.starting_budget_inputbox = InputBox(*starting_budget_inputbox_coords, base_text="Число до триллиона:  ", color=RED, font=self.fonts['small'])

        self.cost_vaccine_textbox = TextBox(*cost_vaccine_textbox_coords, "Укажите стоимость вакцины", color=ORANGE, font=self.fonts['small'])
        self.cost_vaccine_inputbox = InputBox(*cost_vaccine_inputbox_coords, base_text="Число до миллиона:  ", default='1', color=RED, font=self.fonts['small'])


        x_div, y_div = int(self.WIDTH * 0.6) + 2 * padding, int(self.HEIGHT * 0.03) + padding + 60
        dx_div, dy_div = int(self.WIDTH * 0.35) - 2 * padding, 459
        self.div = TextBox(x_div, y_div, dx_div, dy_div, text='', color=GRAY)

        div_padding = 9
        x_div_elem, y_div_elem = x_div + div_padding, y_div + div_padding
        dx_div_elem, dy_div_elem = dx_div - 2 * div_padding, 36
        x_div_input, dx_div_input = x_div_elem + div_padding, dx_div_elem - 2 * div_padding

        div_type_textbox_coords = (x_div_elem, y_div_elem, dx_div_elem, dy_div_elem)
        div_type_selectbox_coords = (x_div_input, y_div_elem + div_padding + dy_div_elem, dx_div_input, dy_div_elem)

        dx_div_selectbar = dx_div_input // 1.5
        x_div_selectbar = x_div_input + (dx_div_input - dx_div_selectbar) // 2
        div_selectbar_coords = (x_div_selectbar, y_div_elem + div_padding + 2 * dy_div_elem, dx_div_selectbar, dy_div_elem)

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

        self.div_type_textbox = TextBox(*div_type_textbox_coords, "Укажите тип города", color=ORANGE, font=self.fonts['small'])
        self.div_type_selectbox = SelectBox(*div_type_selectbox_coords, "",  color=RED, color_clicked=RED, font=self.fonts['small'])

        self.div_population_textbox = TextBox(*div_population_textbox_coords, "Укажите население", color=ORANGE, font=self.fonts['small'])
        self.div_population_inputbox = InputBox(*div_population_inputbox_coords, base_text="Число до триллиона:  ", color=RED, font=self.fonts['small'])

        self.div_infected_textbox = TextBox(*div_infected_textbox_coords, "Укажите количество заражённых", color=ORANGE, font=self.fonts['small'])
        self.div_infected_inputbox = InputBox(*div_infected_inputbox_coords, base_text="Число до триллиона:  ", color=RED, font=self.fonts['small'])

        self.div_vaccinated_textbox = TextBox(*div_vaccinated_textbox_coords, "Укажите количество вакцинированных", color=ORANGE, font=self.fonts['small'])
        self.div_vaccinated_inputbox = InputBox(*div_vaccinated_inputbox_coords, base_text="Число до триллиона:  ", color=RED, font=self.fonts['small'])

        self.div_transport_textbox = TextBox(*div_transport_textbox_coords, "Укажите уровнь транспорта", color=ORANGE, font=self.fonts['small'])
        self.div_transport_inputbox = InputBox(*div_transport_inputbox_coords, base_text="Число от 1 до 100:  ", default=1, color=RED, font=self.fonts['small'])

        self.selectbar = SelectBar(
            *div_selectbar_coords,
            ['мегаполис', 'город', 'посёлок'],
            background_color=WHITE,
            box_color=RED,
            color_clicked=WHITE,
            font=self.fonts['small']
        )


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

    def _clean_data(self) -> None:
        """Очисить данные после симуляции"""
        self.selected_city_index = None
        self.starting_infection = {}
        self.cities_type = []
        self.radius_cities = {}

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
            width = 2 if self.starting_infection[city['name']] else 1
            pygame.draw.circle(self.screen, color_border, (x, y), radius + width)
            pygame.draw.circle(self.screen, color, (x, y), radius)

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

        padding = int(self.WIDTH_PANEL * 0.04)
        textbox_width = int(self.WIDTH_PANEL * 0.88) + padding
        textbox_coords = (self.WIDTH_MAP + padding, padding, textbox_width, 50)
        government_textbox = TextBox(*textbox_coords, text=f"Данные по государству", color=ORANGE, font=self.fonts['small'])
        government_textbox.draw(self.screen)

        stats = [
            f"Больных: {statistics['government']['number_infected']}",
            f"Вакцинированных: {statistics['government']['number_vaccinated']}",
            f"Здоровых: {statistics['government']['population'] - statistics['government']['number_infected'] - statistics['government']['number_vaccinated']}",
            f"Бюджет: {statistics['government']['budget']}",
            f"Стоимость вакцины: {statistics['government']['vaccine_cost']}"
        ]
        y_offset = 50 + 2 * padding
        for i, stat in enumerate(stats):
            text = self.fonts['small'].render(stat, True, BLACK)
            x_offset = self.WIDTH_MAP + (self.WIDTH_PANEL - text.get_width()) // 2
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += 30

        if self.selected_city_index is not None:
            city = statistics['cities'][self.selected_city_index]

            textbox_coords = (self.WIDTH_MAP + padding, y_offset, textbox_width, 50)
            city_textbox = TextBox(*textbox_coords, text=f"Данные по городу {city['name']}", color=ORANGE, font=self.fonts['small'])
            city_textbox.draw(self.screen)

            y_offset += 50 + padding
            city_stats = [
                f"Больных: {city['number_infected']}",
                f"Вакцинированных: {city['number_vaccinated']}",
                f"Здоровых: {city['population'] - city['number_infected'] - city['number_vaccinated']}",
            ]
            for i, stat in enumerate(city_stats):
                text = self.fonts['small'].render(stat, True, BLACK)
                x_offset = self.WIDTH_MAP + (self.WIDTH_PANEL - text.get_width()) // 2
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
        step_text = self.fonts['small'].render(f"Шаг: {self.current_step} из {self.max_step}", True, BLACK)

        self.screen.blit(month_text, (rect_x + 10, rect_y + 10))
        self.screen.blit(week_text, (rect_x + 10, rect_y + 40))
        self.screen.blit(step_text, (rect_x + 10, rect_y + 70))

    def _draw_buttons_simulation(self) -> None:
        """Отображает кнопку для перехода к следующему шагу симуляции."""
        self.exit_button.draw(self.screen)

        if self.current_step + 1 == len(self.simulation.history) and self.current_step < self.max_step:
            self.textbox.draw(self.screen)
            self.spend_budget_button.draw(self.screen)
        if self.current_step != 0:
            self.prev_button.draw(self.screen)
        if self.current_step != self.max_step:
            self.next_button.draw(self.screen)
        self.config_button.draw(self.screen)

    def _draw_setup_menu(self) -> None:
        """Отображает начальное меню для установки параметров симуляции."""
        self.exit_button.draw(self.screen)

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
            self.div.draw(self.screen)

            self.div_type_textbox.draw(self.screen)
            self.div_type_selectbox.set_text(self.selectbar.get_data())
            self.div_type_selectbox.draw(self.screen)

            self.div_population_textbox.draw(self.screen)
            self.div_population_inputbox.draw(self.screen)

            self.div_infected_textbox.draw(self.screen)
            self.div_infected_inputbox.draw(self.screen)

            self.div_vaccinated_textbox.draw(self.screen)
            self.div_vaccinated_inputbox.draw(self.screen)

            self.div_transport_textbox.draw(self.screen)
            self.div_transport_inputbox.draw(self.screen)

        if self.clicked_box == self.div_type_selectbox:
            self.selectbar.draw(self.screen)

    def _handle_events_simulation(self) -> None:
        """Обработчик событий во время симуляции."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.spend_budget_button.error_message = ''
                self.spend_budget_button.active = False

                if self.exit_button.is_clicked(event):
                    pygame.quit()
                    sys.exit()

                elif (self.spend_budget_button.is_clicked(event) and
                    self.current_step + 1 == len(self.simulation.history) and
                    self.current_step < self.max_step):
                    self.spend_budget_button.active = True
                    self.spend_budget_button.text = ''

                elif self.current_step != 0 and self.prev_button.is_clicked(event):
                    self.current_step = max(0, self.current_step - 1)

                elif self.current_step != self.max_step and self.next_button.is_clicked(event):
                    if self.current_step < self.max_step:
                        if self.current_step + 1 == len(self.simulation.history):
                            money = int(self.spend_budget_button.text) if self.spend_budget_button.text != '' else 0
                            self.spend_budget_button.text = ''
                            self.simulation.make_step(money)
                        self.current_step += 1

                elif self.config_button.is_clicked(event):
                    self.simulation_running = False
                    self._clean_data()

                else:
                    clicked = False
                    for index, (_, radius) in enumerate(self.radius_cities.items()):
                        x, y = self._COORDINATES_POINTS[index]
                        distance = ((event.pos[0] - x) ** 2 + (event.pos[1] - y) ** 2) ** 0.5
                        if distance <= radius:
                            clicked = True
                            self.selected_city_index = index
                    if not clicked:
                        self.selected_city_index = None

            elif event.type == pygame.KEYDOWN and self.spend_budget_button.active:
                self.spend_budget_button.error_message == ''

                if event.key == pygame.K_RETURN:
                    self.spend_budget_button.active = False

                elif event.key == pygame.K_BACKSPACE:
                    self.spend_budget_button.text = self.spend_budget_button.text[:-1] if self.spend_budget_button.text != '' else ''

                else:
                    symbol: str = event.unicode
                    if symbol.isdigit():
                        self.spend_budget_button.text += symbol
                        money = int(self.spend_budget_button.text) if self.spend_budget_button.text != '' else 0
                        if self.simulation.government.budget < money:
                            self.spend_budget_button.error_message = "В доступе нет такой суммы денег!"
                            self.spend_budget_button.text = ''
                    else:
                        self.spend_budget_button.error_message = "Только цифры!"
                        self.spend_budget_button.text = ''

    def _check_input_symbol(self, symbol: str) -> None:
        """"Проверка и обработка введённых символов с клавиатуры/"""
        if not isinstance(self.clicked_box, InputBox):
            raise AttributeError("Somthing went wrong.")
        self.clicked_box: InputBox

        if self.clicked_box == self.duration_inputbox:
            if symbol.isdigit():
                self.clicked_box.text += symbol
                if not (1 <= int(self.clicked_box.text) <= 120):
                    self.clicked_box.error_message = "Число из диапазона [1, 120]"
                    self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        elif self.clicked_box == self.starting_month_inputbox:
            if symbol.isdigit():
                self.clicked_box.text += symbol
                if not (1 <= int(self.clicked_box.text) <= 12):
                    self.clicked_box.error_message = "Число из диапазона [1, 12]"
                    self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        elif self.clicked_box == self.number_citis_inputbox :
            if symbol.isdigit():
                self.clicked_box.text += symbol
                if not (1 <= int(self.clicked_box.text) <= 10):
                    self.clicked_box.error_message = "Число из диапазона [1, 10]"
                    self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''
            self._citites_list_control()

        elif self.clicked_box == self.starting_budget_inputbox:
            if symbol.isdigit():
                if self.clicked_box.text != '' or int(symbol) != 0:
                    self.clicked_box.text += symbol
                    if not (0 <= int(self.clicked_box.text) <= 1000000000000):
                        self.clicked_box.error_message = "Число из диапазона [0, 10 ^ 12]"
                        self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        elif self.clicked_box == self.cost_vaccine_inputbox:
            if symbol.isdigit():
                self.clicked_box.text += symbol
                if not (1 <= int(self.clicked_box.text) <= 10000000):
                    self.clicked_box.error_message = "Число из диапазона [1, 10 ^ 6]"
                    self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        elif self.clicked_box == self.div_population_inputbox:
            if symbol.isdigit():
                if self.clicked_box.text != '' or int(symbol) != 0:
                    self.clicked_box.text += symbol
                    if not (0 <= int(self.clicked_box.text) <= 10000000000000):
                        self.clicked_box.error_message = "Число из диапазона [0, 10 ^ 12]"
                        self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        elif self.clicked_box == self.div_infected_inputbox:
            if symbol.isdigit():
                if self.clicked_box.text != '' or int(symbol) != 0:
                    self.clicked_box.text += symbol
                    number = int(self.clicked_box.text)
                    vaccinated = int(self.div_vaccinated_inputbox.get_data())
                    population = int(self.div_population_inputbox.get_data())

                    if not (0 <= number <= 10000000000000):
                        self.clicked_box.error_message = "Число из диапазона [0, 10 ^ 12]"
                        self.clicked_box.text = ''
                    if number + vaccinated > population:
                        self.clicked_box.error_message = "Нельзя превосходить население!"
                        self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        elif self.clicked_box == self.div_vaccinated_inputbox:
            if symbol.isdigit():
                if self.clicked_box.text != '' or int(symbol) != 0:
                    self.clicked_box.text += symbol
                    number = int(self.clicked_box.text)
                    infected = int(self.div_infected_inputbox.get_data())
                    population = int(self.div_population_inputbox.get_data())

                    if not (0 <= number <= 10000000000000):
                        self.clicked_box.error_message = "Число из диапазона [0, 10 ^ 12]"
                        self.clicked_box.text = ''
                    if number + infected > population:
                        self.clicked_box.error_message = "Нельзя превосходить население!"
                        self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        elif self.clicked_box == self.div_transport_inputbox:
            if symbol.isdigit() and (self.clicked_box.text != '' or int(symbol) != 0):
                self.clicked_box.text += symbol
                if not (1 <= int(self.clicked_box.text) <= 100):
                    self.clicked_box.error_message = "Число из диапазона [1, 100]"
                    self.clicked_box.text = ''
            else:
                self.clicked_box.error_message = "Только цифры!"
                self.clicked_box.text = ''

        else:
            raise AttributeError("Somthing went wrong.")

    def _add_div_information(self) -> None:
        """Сохраняет введённые данные по городу."""
        if self.clicked_selectbox is not None:
            city = self.cities_data[self.cities_selectboxes.index(self.clicked_selectbox)]

            if self.selectbar.get_data() == 'мегаполис':
                city['city_type'] = 'megapolis'
            elif self.selectbar.get_data() == 'город':
                city['city_type'] = 'medium'
            elif self.selectbar.get_data() == 'посёлок':
                city['city_type'] = 'town'
            else:
                raise ValueError("Somthing went wrong.")

            city['population'] = int(self.div_population_inputbox.get_data())
            city['number_infected'] = int(self.div_infected_inputbox.get_data())
            city['number_vaccinated'] = int(self.div_vaccinated_inputbox.get_data())
            city['transport'] = float(self.div_transport_inputbox.get_data()) / 100

            self.div_population_inputbox.text = ''
            self.div_infected_inputbox.text = ''
            self.div_vaccinated_inputbox.text = ''
            self.div_transport_inputbox.text = ''

    def _citites_list_control(self) -> None:
        """Проводит обработку списков, контролирующих ввод и храненние данных по городам."""
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
            self.cities_selectboxes.append(SelectBox(*city_coords, f"Город {index}", font=self.fonts['small'], color=RED, color_clicked=WHITE))
            self.cities_data.append(government_data['cities_data'][index - 1])

    def _set_default_values(self) -> None:
        """Установка параметров по умолчанию для кнопок."""
        city = self.cities_data[self.cities_selectboxes.index(self.clicked_selectbox)]

        if city['city_type'] == "megapolis":
            self.selectbar.choose("мегаполис")
        elif city['city_type'] == "medium":
            self.selectbar.choose("город")
        elif city['city_type'] == "town":
            self.selectbar.choose("посёлок")
        else:
            raise ValueError("Somthing went wrong.")
        self.div_population_inputbox.default = str(city['population'])
        self.div_infected_inputbox.default = str(city['number_infected'])
        self.div_vaccinated_inputbox.default = str(city['number_vaccinated'])
        self.div_transport_inputbox.default = str(int(100 * city['transport']))

    def _handle_events_setuping(self) -> None:
        """Обработчик событий во время конфигурации симуляции."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.exit_button.is_clicked(event):
                    pygame.quit()
                    sys.exit()

                elif (self.clicked_box is not None and
                      self.clicked_box != self.div_type_selectbox):
                    self.clicked_box.error_message = ''
                    self.clicked_box = None

                if self.clicked_box == self.div_type_selectbox:
                    if self.selectbar.is_clicked(event):
                        self.selectbar.click_option(event)
                    else:
                        self.clicked_box = None
                    self._add_div_information()

                elif self.duration_inputbox.is_clicked(event):
                    self.clicked_box = self.duration_inputbox

                elif self.starting_month_inputbox.is_clicked(event):
                    self.clicked_box = self.starting_month_inputbox

                elif self.number_citis_inputbox.is_clicked(event):
                    self.clicked_box = self.number_citis_inputbox

                elif self.starting_budget_inputbox.is_clicked(event):
                    self.clicked_box = self.starting_budget_inputbox

                elif self.cost_vaccine_inputbox.is_clicked(event):
                    self.clicked_box = self.cost_vaccine_inputbox

                elif self.div_type_selectbox.is_clicked(event):
                    if self.clicked_box != self.div_type_selectbox:
                        self.clicked_box = self.div_type_selectbox

                elif self.div_population_inputbox.is_clicked(event):
                    self.clicked_box = self.div_population_inputbox

                elif self.div_infected_inputbox.is_clicked(event):
                    self.clicked_box = self.div_infected_inputbox

                elif self.div_vaccinated_inputbox.is_clicked(event):
                    self.clicked_box = self.div_vaccinated_inputbox

                elif self.div_transport_inputbox.is_clicked(event):
                    self.clicked_box = self.div_transport_inputbox

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
                            self._set_default_values()
                            break

            elif (event.type == pygame.KEYDOWN and
                  self.clicked_box is not None and
                  self.clicked_box != self.div_type_selectbox):
                self.clicked_box.error_message = ''

                if event.key == pygame.K_RETURN:
                    self.clicked_box = None

                elif event.key == pygame.K_BACKSPACE and self.clicked_box != self.div_type_selectbox:
                    self.clicked_box.text = self.clicked_box.text[:-1] if self.clicked_box.text != '' else ''
                    if self.clicked_box == self.number_citis_inputbox:
                        self._citites_list_control()

                else:
                    symbol: str = event.unicode
                    self._check_input_symbol(symbol)

    def _collect_data(self) -> None:
        """Сбор введённых данных пользователем."""
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
                month, week = self.simulation.start_month + self.current_step // 4, self.current_step % 4 + 1

                self._draw_cities()
                self._draw_legend()
                self._draw_month_week(month, week)
                self._draw_statistics()
                self._draw_buttons_simulation()

                self._handle_events_simulation()
            else:
                self._draw_setup_menu()

                self._handle_events_setuping()


            pygame.display.flip()
            self.clock.tick(30)
