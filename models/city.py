import math
from typing import Dict, TypedDict


VACCINATED_RATE_3_WEEKS = 0.8
VACCINATED_RATE_2_WEEKS = 0.15
VACCINATED_RATE_1_WEEKS = 1 - VACCINATED_RATE_3_WEEKS - VACCINATED_RATE_2_WEEKS
INFECTED_RATE_3_WEEKS = 0.15
INFECTED_RATE_2_WEEKS = 0.6
INFECTED_RATE_1_WEEKS = 1 - INFECTED_RATE_3_WEEKS - INFECTED_RATE_2_WEEKS


BASE_RATE         = 1.5
W_TYPE_CITY       = lambda x: {'megapolis': 1.5, 'medium': 1.25, 'town': 1}[x]
W_MONTH           = lambda x: 1.5 if 9 <= x <= 3 else 1


class CityData(TypedDict):
    name: str
    city_type: str
    population: int
    transport: float
    number_vaccinated: int
    number_infected: int


class CityStatisticsData(TypedDict):
    name: str
    population: int
    number_vaccinated: int
    number_infected: int
    number_innocent: int
    number_workers: int


class City:
    def __init__(self, name: str, city_type: str, population: int, transport: float,
                 number_vaccinated: int = 0, number_infected: int = 0) -> None:
        """
        Инициализация города.

        :param name: Название города.
        :param city_type: Тип города ("megapolis", "medium", "town").
        :param population: Численность населения.
        :param transport: Уровень транспорта (0.0 - 1.0).
        :param number_vaccinated: Начальное число вакцин.
        :param number_infected: Начальное число заболевших.
        """
        if not (0 <= transport <= 1):
            raise ValueError("transport must be in [0, 1]")
        if city_type not in ["megapolis", "medium", "town"]:
            raise ValueError("city_type must be 'megapolis', 'medium' or 'town'")

        self.name = name
        self.population = population
        self.transport = transport
        self.city_type = city_type

        self.vaccinated: Dict[int, int] = {
            3: int(VACCINATED_RATE_3_WEEKS * number_vaccinated),
            2: int(VACCINATED_RATE_2_WEEKS * number_vaccinated),
            1: int(VACCINATED_RATE_1_WEEKS * number_vaccinated),
        }

        self.infected: Dict[int, int] = {
            3: int(INFECTED_RATE_3_WEEKS * number_infected),
            2: int(INFECTED_RATE_2_WEEKS * number_infected),
            1: int(INFECTED_RATE_1_WEEKS * number_infected),
        }

    @property
    def number_vaccinated(self) -> int:
        """Возвращает общее число вакцинированных."""
        return sum(self.vaccinated.values())

    @property
    def number_infected(self) -> int:
        """Возвращает общее число заболевших."""
        return sum(self.infected.values())

    @property
    def number_innocent(self) -> int:
        """Возвращает число непривитых."""
        return self.population - self.number_infected - self.number_vaccinated

    @property
    def number_workers(self) -> int:
        """Возвращает число работающих людей."""
        return self.population - self.number_infected

    def _allocate_vaccines(self, number_vaccines: int) -> None:
        """Выделяет вакцины для города."""
        number_innocent = self.number_innocent
        for week in range(1, 3):
            self.vaccinated[week] = self.vaccinated[week + 1]
        self.vaccinated[3] = min(number_vaccines, number_innocent)

    def _recover_people(self) -> None:
        """Обновляет данные о выздоровевших людях."""
        for week in range(1, 3):
            self.infected[week] = self.infected[week + 1]
        self.infected[3] = 0

    def _spread_infection(self, month: int, government_factor: float = 0) -> None:
        """Моделирует распространение инфекции."""
        def modeling_spread_infection() -> int:
            seasonal_factor = W_MONTH(month)
            city_factor =  W_TYPE_CITY(self.city_type)
            transport_factor = self.transport
            vaccine_effect = math.exp(-self.number_vaccinated / self.population * 5)
            infection_growth = (self.number_infected / self.population) ** 0.5
            infection_growth = government_factor if infection_growth == 0 else infection_growth

            new_infected = int(
                self.number_innocent *
                BASE_RATE *
                seasonal_factor *
                transport_factor *
                vaccine_effect *
                infection_growth *
                city_factor
            )
            new_infected = max(0, min(new_infected, self.number_innocent))
            return new_infected

        new_infected = modeling_spread_infection()
        self.infected[3] += int(INFECTED_RATE_3_WEEKS * new_infected)
        self.infected[2] += int(INFECTED_RATE_2_WEEKS * new_infected)
        self.infected[1] += int(INFECTED_RATE_1_WEEKS * new_infected)

    def update_state(self, month: int, number_vaccines: int, government_factor: float = 0) -> None:
        """Обновляет состояние города: вакцинация, распространение, выздоровление."""
        self._allocate_vaccines(number_vaccines)
        self._recover_people()
        self._spread_infection(month, government_factor)

    def get_statistics(self) -> CityStatisticsData:
        """Возвращает статистику по городу."""
        city_statistics = {
            "name": self.name,
            "population": self.population,
            "number_vaccinated": self.number_vaccinated,
            "number_infected": self.number_infected,
            "number_innocent": self.number_innocent,
            "number_workers": self.number_workers,
        }
        return city_statistics
