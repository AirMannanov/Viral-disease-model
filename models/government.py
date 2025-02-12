from .city import City, CityData, CityStatisticsData
from typing import List, Dict, TypedDict


TAX_PER_PRESON = 1.5
TAX_RATE_PAYMENT = 0.65


class GovernmentData(TypedDict):
    name: str
    budget: int
    vaccine_cost: int
    cities_data: List[CityData]


class GovernmentStatisticsData(TypedDict, CityStatisticsData):
    budget: int
    vaccine_cost: int


class StatisticsData(TypedDict):
    government: GovernmentStatisticsData
    cities: List[CityStatisticsData]


class Government:
    def __init__(self, name: str, budget: int, vaccine_cost: int, cities_data: List[CityData]) -> None:
        """
        Инициализация государства.

        :param cities: Список городов.
        :param budget: Бюджет на вакцинацию.
        :param vaccine_cost: Стоимость одной вакцины.
        :param cities_data: Список параметров городов.
        """
        if budget < 0:
            raise ValueError("Budget cannot be negative")
        if vaccine_cost <= 0:
            raise ValueError("Vaccine cost must be positive")

        self.name = name
        self.budget = budget
        self.vaccine_cost = vaccine_cost
        self.cities = [City(**params) for params in cities_data]
        self.government_factor = (self.number_infected / self.population) ** 0.5

    def _update_budget(self) -> None:
        """Обновляет бюджет с учётом оплаты налогов."""
        self.budget += int(TAX_RATE_PAYMENT * TAX_PER_PRESON * sum(city.number_workers for city in self.cities))

    def _update_cities_state(self, month: int, vaccines: Dict[str, int]) -> None:
        """
        Обновляет состояние всех городов, распределяя вакцины и моделируя заражение.

        :param month: Текущий месяц.
        :param vaccines: Распределение вакцин по городам {"город": кол-во вакцин}.
        """
        for city in self.cities:
            num_vaccines = vaccines.get(city.name, 0)
            if self.budget < num_vaccines * self.vaccine_cost:
                raise ValueError(f"Недостаточно бюджета для распределения {num_vaccines} вакцин в городе {city.name}. \
                                 Требуется: {num_vaccines * self.vaccine_cost}, доступно: {self.budget}")
            self.budget -= num_vaccines * self.vaccine_cost
            city.update_state(month, num_vaccines, self.government_factor)

    def update_state(self, month: int, vaccines: Dict[str, int]) -> None:
        """
        Возвращает новое состояние государства после очередного шага моделирования.

        :param month: Текущий месяц.
        :param vaccines: Распределение вакцин по городам.
        :return: Обновлённое состояние государства.
        """
        self._update_budget()
        self._update_cities_state(month, vaccines)
        self.government_factor = (self.number_infected / self.population) ** 0.5

    @property
    def population(self) -> int:
        """Возвращает число жителей государства."""
        return sum(city.population for city in self.cities)

    @property
    def number_vaccinated(self) -> int:
        """Возвращает общее число вакцинированных."""
        return sum(city.number_vaccinated for city in self.cities)

    @property
    def number_infected(self) -> int:
        """Возвращает общее число заболевших."""
        return sum(city.number_infected for city in self.cities)

    @property
    def number_innocent(self) -> int:
        """Возвращает число непривитых."""
        return sum(city.number_innocent for city in self.cities)

    @property
    def number_workers(self) -> int:
        """Возвращает число работающих людей."""
        return sum(city.number_workers for city in self.cities)

    def get_statistics(self) -> StatisticsData:
        """Возвращает статистику по государству c городами."""
        government_statistics = {
            "name": self.name,
            "population": self.population,
            "number_vaccinated": self.number_vaccinated,
            "number_infected": self.number_infected,
            "number_innocent": self.number_innocent,
            "number_workers": self.number_workers,
            "budget": self.budget,
            "vaccine_cost": self.vaccine_cost,
        }
        cities_statistics = [city.get_statistics() for city in self.cities]
        return {"government": government_statistics, "cities": cities_statistics}
