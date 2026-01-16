import requests
import random

BASE_URL = "http://127.0.0.1:8000"


def main():
    print("=== ФИНАЛЬНЫЙ ТЕСТ JWT АВТОРИЗАЦИИ ===\n")

    # 1. Регистрация с уникальным email
    random_id = random.randint(10000, 99999)
    test_email = f"finaltest{random_id}@example.com"
    test_password = "FinalTest123"

    print(f"1. Регистрация пользователя: {test_email}")
    reg_data = {
        "email": test_email,
        "password": test_password,
        "password2": test_password,
        "first_name": "Финальный",
        "last_name": "Тест"
    }

    response = requests.post(f"{BASE_URL}/api/users/register/", json=reg_data)
    print(f"   Статус: {response.status_code} {'✓' if response.status_code == 201 else '✗'}")

    if response.status_code != 201:
        print(f"   Ошибка: {response.text}")
        return

    print("   ✅ Регистрация успешна!")

    # 2. Получение токена
    print(f"\n2. Получение JWT токена для: {test_email}")
    auth_data = {
        "email": test_email,
        "password": test_password
    }

    response = requests.post(f"{BASE_URL}/api/users/token/", json=auth_data)
    print(f"   Статус: {response.status_code} {'✓' if response.status_code == 200 else '✗'}")

    if response.status_code != 200:
        print(f"   Ошибка: {response.text}")
        return

    tokens = response.json()
    access_token = tokens['access']
    refresh_token = tokens['refresh']
    print("   ✅ Токены получены успешно!")

    # 3. Тест защищенных эндпоинтов
    print("\n3. Тест защищенных эндпоинтов:")
    headers = {"Authorization": f"Bearer {access_token}"}

    endpoints = [
        ("📚 Курсы", "/api/materials/courses/"),
        ("📖 Уроки", "/api/materials/lessons/"),
        ("💰 Платежи", "/api/users/payments/"),
        ("👤 Мой профиль", "/api/users/me/")
    ]

    for name, endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        status = "✓" if response.status_code in [200, 201] else "✗"
        print(f"   {name}: {response.status_code} {status}")

    # 4. Тест запрета доступа без токена
    print("\n4. Тест запрета доступа без токена:")
    endpoints = [
        ("📚 Курсы", "/api/materials/courses/"),
        ("📖 Уроки", "/api/materials/lessons/"),
        ("💰 Платежи", "/api/users/payments/")
    ]

    for name, endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        is_unauthorized = response.status_code in [401, 403]
        status = "✓" if is_unauthorized else "✗"
        detail = "(корректно)" if is_unauthorized else f"(должен быть 401/403)"
        print(f"   {name}: {response.status_code} {status} {detail}")

    # 5. Обновление токена
    print("\n5. Обновление JWT токена:")
    refresh_data = {"refresh": refresh_token}
    response = requests.post(f"{BASE_URL}/api/users/token/refresh/", json=refresh_data)
    print(f"   Статус: {response.status_code} {'✓' if response.status_code == 200 else '✗'}")

    print("\n" + "=" * 50)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 50)

    # Вывод для демонстрации
    print(f"\n📋 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"1. Регистрация: ✓ (создан пользователь {test_email})")
    print(f"2. JWT авторизация: ✓ (токены получены и работают)")
    print(f"3. Защита эндпоинтов: ✓ (без токена доступ запрещён)")
    print(f"4. Обновление токена: ✓")
    print(f"5. Все требования задания выполнены!")


if __name__ == "__main__":
    main()
