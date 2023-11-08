# flask
Данный проект является учебным сайтом flsite с возможностью создания и чтения постов, а также с регистрацией на сайте. 
В панели администратора можно посмотреть список зарегистрированных пользователей и добавленных статей. 

### Технологический Стек
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)

## Установить venv 
``` python3.9 -m venv venv ```

## Активировать venv 
``` source venv/bin/activate ```

## Обновить менеджер пакетов pip 
``` python3 -m pip install --upgrade pip ```

## Установить все зависимости из requirements 
``` pip install -r requirements.txt ```

## Запустить проект 
``` python3 flsite.py ```

### Перед запуском проекта
Перед запуском проекта необходимо настроить меню проекта через DB Browser for SQLite.
Первоначально в терминале выполните команду python3. Введите в консоле `from flsite import create_db`. Далее нажимаем enter и вводим следующую команду `create_db()`.
После запуска приложения для работы с базой данных, необходимо открыть базу данных и выбрать файл flsite.db. 
В появившемся поле "Данные" заполняем таблицу mainmenu:
1. title - Главная, url - '/'
2. title - Добавить статью, url - 'add_post'
Теперь сайт готов к работе. 

### Загрузка изображения в профиль
Загрузка изображений в профиле пользователя доступна в разрешении png.

[Flask’s documentation](https://flask.palletsprojects.com/en/3.0.x/)
[Документация по Flask на русском](https://flask-russian-docs.readthedocs.io/ru/0.10.1/)

Автор: Ефремова Каролина