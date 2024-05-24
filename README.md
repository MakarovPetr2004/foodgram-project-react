# Foodgram :avocado:
_Foodgram_ — сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит вам сформировать список продуктов, которые необходимо купить для приготовления выбранных блюд.

## Содержимое
* [Локальный запуск](#локальный-запуск)
* [Технологии](#технологии)
* [Авторы](#авторы)


## Локальный запуск
- Перейдите в папку _infra_ и запустите docker compose: ```docker compose up --build```
- Выполните миграции:
```sh 
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```
- Соберите статику для _backend_
```sh 
docker compose exec backend python manage.py collectstatic
```

## Технологии:
- Python 3.9
- Django 3.2.3
- Pillow 9.0.0
- DRF 3.12.4
- Djoser 2.2.0

## Авторы
* [Макаров Пётр](https://github.com/MakarovPetr2004)


