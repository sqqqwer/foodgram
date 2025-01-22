# Foodgram

## Содержание
- [1. О сервисе](#1-о-сервисе)
- [2. Функционал](#2-функционал)
- [3. Стек технологий](#3-стек-технологий)
- [4. Установка проекта](#4-установка-проекта)
- [5. Документация](#5-документация)
- [6. Регистрация и авторизация](#6-регистрация-и-авторизация-пользователей)
- [7. Примеры запросов](#7-примеры-запросов)
- [8. Авторы](#8-авторы)

## 1. О сервисе
С помощью этого сервиса можно создавать рецепты и делиться ими.

## 2. Функционал сервиса
- Реализована система регистрации и аутентификации пользователей
- Можно поменять аватарку
- Авторизованные пользователи могут создавать рецепты
- Рецепты можно добавлять в корзину или в избранное
- Можно скачивать список ингредиентов со всех рецептов в корзине
- Есть возможность подписки на другого пользователя
- Рецепты можно фильтровать по тегам
- Есть админ панель

## 3. Стек технологий
- Docker
- Nginx
- CI/CD service (GitHub Actions)
### Бэкенд
- Python 3.10
- Django
- Django REST FrameWork
- Djoser
- Gunicorn
- DRF extra fields
### Фронтенд
- Javascript
- Node.js
- React


## 4. Установка проекта
- Клонируйте репозиторий
```shell
git clone https://github.com/sqqqwer/foodgram.git
```
- Перейдите в папку infra
```shell
cd foodgram/infra/
```
- Запустите docker

(если у вас linux или macOS, то перед docker пишите sudo)
- Запустите проект
```shell
docker compose up -d
```
- Примените миграции
```shell
docker compose exec backend python manage.py migrate
```
- Добавьте ингредиенты и теги в ДБ
```shell
docker compose exec backend python manage.py load_from_csv data/
```
- Соберите статические файлы бэкенд приложения
```shell
docker compose exec backend python manage.py collectstatic
```
- Перенесите статические файлы в volume со статикой
```shell
docker compose exec cp -r /app/collected_static/. /backend_static/build/static/
```

## 5. Документация
Для просмотра полной документации перейдите на http://localhost/api/docs/

## 6. Регистрация и авторизация пользователей
### Регистрация
Запрос:
```
POST http://localhost/api/users/
```
```json
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "Qwerty123"
}
```
Ответ:

*Cоздаётся и возвращается новый пользователь*
```json
{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов"
}
```
### Авторизация
Запрос:
```
POST http://localhost/api/auth/token/login/
```
```json
{
    "password": "Qwerty123",
    "email": "vpupkin@yandex.ru"
}
```
Ответ:

*Возвращает токен*
```json
{
    "auth_token": "8cs81ed89fd6527f3d56c3a9v0ed7847e6f0bdc2"
}
```


## 7. Примеры запросов

### Добавление Аватара
Запрос:
```
GET http://localhost/api/users/me/avatar/
Authorization: Token 8cs81ed89fd6527f3d56c3a9v0ed7847e6f0bdc2
```
```json
{
    "avatar": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
}
```

Ответ:
```json
{
    "avatar": "http://localhost/media/users/image.png"
}
```

### Создание рецепта
Запрос:
```
POST http://localhost/api/recipes/
Authorization: Token 8cs81ed89fd6527f3d56c3a9v0ed7847e6f0bdc2
```
```json
{
    "ingredients": [
        {
            "id": 1123,
            "amount": 10
        }
    ],
    "tags": [
        0
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1
}
```
Ответ:

*Cоздаётся и возвращается новый Рецепт*
```json
{
    "id": 0,
    "tags": [
        {
            "id": 0,
            "name": "Завтрак",
            "slug": "breakfast"
        }
    ],
    "author": {
        "email": "vpupkin@yandex.ru",
        "id": 0,
        "username": "vasya.pupkin",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://localhost/media/users/image.png"
    },
    "ingredients": [
        {
            "id": 1123,
            "name": "Картофель отварной",
            "measurement_unit": "г",
            "amount": 10
        }
    ],
    "is_favorited": true,
    "is_in_shopping_cart": true,
    "name": "string",
    "image": "http://localhost/media/recipes/images/image.png",
    "text": "string",
    "cooking_time": 1
}
```

### Подписка на пользователя
Запрос:
```
POST http://localhost/api/users/0/subscribe/
Authorization: Token asdasd87asdasd89asasdfv0ed7847e6f0bdc2
```
Ответ:
```json
{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": true,
    "recipes": [
        {
            "id": 0,
            "name": "string",
            "image": "http://localhost/media/recipes/images/image.png",
            "cooking_time": 1
        }
    ],
    "recipes_count": 1,
    "avatar": "http://localhost/media/users/image.png"
}
```

## 8. Авторы
- _Чернявский Владислав_
- _Команда Яндекс практикума_
