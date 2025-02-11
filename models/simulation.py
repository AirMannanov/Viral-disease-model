from .government import Government, GovernmentData, StatisticsData
from typing import List, Dict

class Simulation:
    def __init__(self, months: int, start_month: int,
                 government_data: GovernmentData,
                 user_play: bool = True) -> None:
        """
        Инициализация симуляции.

        :param months: Количество месяцев, на которое запускается симуляция.
        :param start_month: Номер месяца, с которого начинается симуляция.
        :param government_data: Параметры правительства.
        :param user_play: Флаг, указывающий на ручное или автоматическое распределение вакцин.
        """
        self.months = months
        self.current_month = start_month
        self.current_week = 0
        self.government = Government(**government_data)
        self.allocate_vaccines = self._user_allocate_vaccines if user_play else self._auto_allocate_vaccines
        self.history: List[StatisticsData] = [] # Статистика по всем шагам симуляции

    def _auto_allocate_vaccines(self) -> Dict[str, int]:
        """
        Определяет распределение вакцин по городам на текущий шаг.
        :return: Словарь {название_города: кол-во вакцин}.
        """
        allocation = {}
        can_vaccinate_rate = self.government.budget // self.government.vaccine_cost / self.government.population
        for city in self.government.cities:
            allocation[city.name] = int(can_vaccinate_rate * city.population)

        return allocation

    def _user_allocate_vaccines(self) -> Dict[str, int]:
        """
        Запрашивает у пользователя распределение вакцин по городам на текущий шаг.
        :return: Словарь {название_города: кол-во вакцин}.
        """
        pass

    def make_step(self):
        """Выполняет один шаг симуляции (неделя)."""
        vaccine_distribution = self.allocate_vaccines()
        self.government.update_state(self.current_month, vaccine_distribution)

        self.current_week += 1
        if self.current_week % 4 == 0:
            self.current_month = (self.current_month + 1) % 12

    def run(self):
        """Запускает симуляцию."""
        for _ in range(self.months * 4):
            self.make_step()
            self.history.append(self.government.get_statistics())
