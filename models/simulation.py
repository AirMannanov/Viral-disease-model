from .government import Government, GovernmentData, StatisticsData
from typing import List, Dict

class Simulation:
    def __init__(self, months: int, start_month: int,
                 government_data: GovernmentData) -> None:
        """
        Инициализация симуляции.

        :param months: Количество месяцев, на которое запускается симуляция.
        :param start_month: Номер месяца, с которого начинается симуляция.
        :param government_data: Параметры правительства.
        :param user_play: Флаг, указывающий на ручное или автоматическое распределение вакцин.
        """
        self.months = months
        self.start_month = start_month
        self.current_month = start_month
        self.current_week = 0
        self.government = Government(**government_data)
        self.history: List[StatisticsData] = [self.government.get_statistics()] # Статистика по всем шагам симуляции

    def _allocate_vaccines(self, money: int) -> Dict[str, int]:
        """
        Определяет распределение вакцин по городам на текущий шаг.

        :param money: Доступный бюджет.
        :return: Словарь {название_города: кол-во вакцин}.
        """
        if money > self.government.budget:
            raise ValueError("Недостаточно бюджета для распределения вакцин.")

        allocation = {}
        can_vaccinate_rate = money / self.government.vaccine_cost / self.government.population
        for city in self.government.cities:
            allocation[city.name] = int(can_vaccinate_rate * city.population)

        return allocation

    def make_step(self, money: int) -> None:
        """
        Выполняет один шаг симуляции (неделя).

        :param money: Количество денег для вакцин.
        """
        vaccine_distribution = self._allocate_vaccines(money)
        self.government.update_state(self.current_month, vaccine_distribution)

        self.current_week += 1
        if self.current_week % 4 == 0:
            self.current_month = (self.current_month + 1) % 12

        self.history.append(self.government.get_statistics())
