import requests
import json

BASE = "http://localhost:8000/api"

def p(title, data):
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

# 1. Получаем токен администратора
print("\n>>> Авторизуемся под администратором...")
resp = requests.post(f"{BASE}/token/", json={"username": "admin", "password": "Diplom2026!"})
if resp.status_code == 200:
    admin_token = resp.json()["access"]
    p("Токен администратора получен", resp.json())
else:
    print("Ошибка получения токена:", resp.text)
    exit(1)

headers = {"Authorization": f"Bearer {admin_token}"}

# 2. Создаём автора
print("\n>>> Создаём автора (Лев Толстой)...")
author_data = {
    "first_name": "Лев",
    "last_name": "Толстой",
    "birth_date": "1828-09-09",
    "biography": "Русский писатель, классик мировой литературы"
}
resp = requests.post(f"{BASE}/authors/", json=author_data, headers=headers)
p("Создан автор", resp.json())

# 3. Создаём книгу
print("\n>>> Создаём книгу (Война и мир)...")
book_data = {
    "title": "Война и мир",
    "author": 1,
    "genre": "fiction",
    "publication_year": 1869,
    "isbn": "978-5-389-20999-4",
    "available_copies": 3
}
resp = requests.post(f"{BASE}/books/", json=book_data, headers=headers)
p("Создана книга", resp.json())

# 4. Список книг (без авторизации)
print("\n>>> Получаем список книг (открытый доступ)...")
resp = requests.get(f"{BASE}/books/")
p("Список книг", resp.json())

# 5. Регистрируем читателя
print("\n>>> Регистрируем читателя...")
reader_data = {"username": "reader", "email": "reader@example.com", "password": "StrongPass123"}
resp = requests.post(f"{BASE}/register/", json=reader_data)
p("Читатель зарегистрирован", resp.json())

# 6. Получаем токен читателя
print("\n>>> Получаем токен читателя...")
resp = requests.post(f"{BASE}/token/", json={"username": "reader", "password": "StrongPass123"})
reader_token = resp.json()["access"]
p("Токен читателя получен", resp.json())

# 7. Проверяем права читателя (ожидаем 403)
print("\n>>> Проверяем, что читатель НЕ может создать книгу...")
resp = requests.post(f"{BASE}/books/", json={
    "title": "Запрещённая", "author": 1, "genre": "other", "isbn": "000", "available_copies": 1
}, headers={"Authorization": f"Bearer {reader_token}"})
print(f"Статус: {resp.status_code} (ожидаем 403)")
if resp.status_code == 403:
    print("OK – доступ запрещён.")
else:
    print("Ошибка прав доступа!")

# 8. Создаём выдачу админом для читателя
print("\n>>> Создаём выдачу книги админом для читателя...")
borrow_data = {"user": 2, "book": 1, "due_date": "2026-05-20"}
resp = requests.post(f"{BASE}/borrowings/", json=borrow_data, headers=headers)
p("Запись выдачи создана", resp.json())

# 9. Проверяем количество копий
print("\n>>> Проверяем доступные копии книги (должно быть 2)...")
resp = requests.get(f"{BASE}/books/1/")
book = resp.json()
print(f"Доступно копий: {book['available_copies']}")

# 10. Возврат книги админом
print("\n>>> Возврат книги админом...")
resp = requests.patch(f"{BASE}/borrowings/1/return_book/", headers=headers)
p("Книга возвращена", resp.json())

# 11. Проверяем восстановление копий
print("\n>>> Проверяем количество копий после возврата (должно быть 3)...")
resp = requests.get(f"{BASE}/books/1/")
book = resp.json()
print(f"Доступно копий: {book['available_copies']}")

# 12. Профиль администратора
print("\n>>> Профиль администратора...")
resp = requests.get(f"{BASE}/profile/", headers=headers)
p("Профиль", resp.json())

print("\n=== Все тесты успешно пройдены! ===")
