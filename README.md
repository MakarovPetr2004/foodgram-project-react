# Foodgram
_Foodgram_ — a website on which users will publish recipes, add other people's recipes to favorites and subscribe to publications of other authors. Users of the site will also have access to the “Shopping List” service. It will allow you to create a list of products that you need to buy to prepare the selected dishes.

## Table of contents
* [Website and Admin data](#website-and-admin-data)
* [Local launch](#local-launch)
* [Technologies](#technologies)
* [Author](#authors)

## Website and Admin data
- Link: https://foodgram-makarov.ddns.net/
- Login: admin@admin.com
- Password: admin

## Local launch
- Go to _infra_ folder and type: ```docker compose up --build```
- Make migrations:
```sh 
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```
- Collect static for _backend_
```sh 
docker compose exec backend python manage.py collectstatic
```

## Technologies
- Python 3.9
- Django 3.2.3
- Pillow 9.0.0
- DRF 3.12.4
- Djoser 2.2.0

## Authors
* [Makarov Petr](https://github.com/Nintiko)
* [Yandex Practicum](https://github.com/yandex-praktikum)

