## Django сервис для парсинга abuse и их получения с помощью API ##
***
### Установка ###
1. `git clone https://github.com/kevlinsky/akvelon_python_internship_3_Artyom_Elin.git`
2. `python -m venv venv`
3. `source venv/bin/activate`
4. `export PYTHONPATH="path_to_project"`
5. `pip install -r requirements.txt`
6. Добавить 5 переменных среды:  
   1. `DB_NAME`
   2. `DB_USER`
   3. `DB_USER_PASSWORD`
   4. `DB_HOST`
   5. `DB_PORT`
7. `python manage.py makemigrations`
8. `python manage.py migrate`
9. `python manage.py createsuperuser`
---
### Запуск и использование ###
1. Запуск сервиса: `python manage.py runserver localhost:8000`
3. Документация к API: `http://localhost:8000/api/swagger/`
    * Для использования большинства методов API вам потребуется авторизация по JWT токен (см. раздел `token` в документации к API)
4. Админ панель: `http://localhost:8000/admin/`

## Fibonacci util ##
***
### Запуск ###
1. Перейдите в корневую папку проекта
2. Выполните команду `python utils.py fibonacci *число*`
### Помощь ###
Для показа `help` сообщения выполните команду  
```python utils.py fibonacci help```