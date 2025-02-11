from models import Simulation

city_1 = {
    "name": "Moscow",
    "city_type": "megapolis",
    "population": 120,
    "internal_transport": 0.9,
    "external_transport": 0.8,
    "number_infected": 100
}
city_2 = {
    "name": "Perm",
    "city_type": "town",
    "population": 20,
    "internal_transport": 0.6,
    "external_transport": 0.3,
    "number_infected": 18
}
government_data = {
    "name": "Russia",
    "budget": 0,
    "vaccine_cost": 2,
    "cities_data": [city_1, city_2]
}

simulation = Simulation(months=1, start_month=9, government_data=government_data, user_play=False)
simulation.run()

print("\nСтатистика после завершения симуляции:")
for step, stats in enumerate(simulation.history):
    print(f"\nШаг {step + 1}:")
    print(f"  Бюджет: {stats['government']['budget']}")
    print(f"  Общее число вакцинированных: {stats['government']['number_vaccinated']}")
    print(f"  Общее число заболевших: {stats['government']['number_infected']}")
    print(f"  Общее число здоровых непривитых: {stats['government']['number_innocent']}")
    print(f"  Общее число работающих: {stats['government']['number_workers']}")

    print("\n  Статистика по городам:")
    for city_stats in stats['cities']:
        print(f"    Город: {city_stats['name']}")
        print(f"      Население: {city_stats['population']}")
        print(f"      Вакцинированные: {city_stats['number_vaccinated']}")
        print(f"      Заболевшие: {city_stats['number_infected']}")
        print(f"      Здоровые непривитые: {city_stats['number_innocent']}")
        print(f"      Работающие: {city_stats['number_workers']}")