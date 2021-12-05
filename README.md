# aitarget_test_task
Тестовое задание для aitarget
Проект позволяет вести библиотеку книг авторов и организовывать 
подписки на них

# Клонирование проекта

```
git clone https://github.com/cianoid/aitarget_test_task.git
cd aitarget_test_task
```

# Запуск проекта

Есть два контейнера:
* dev (запускается dev-сервер + postgresql)
* production (gunicorn + nginx + postrgresql)

## dev-контейнер

### .env
Создать файл .env в папке проекта (aitarget_test_task) по шаблону.
Необходимо заполнить недостающие данные

```
DEBUG=1
ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
SECRET_KEY=secret-django-key
POSTGRES_DB=mylibrary
POSTGRES_USER=mylibrary_user
POSTGRES_PASSWORD=mylibrary_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE=postgres
LC_COLLATE=ru_RU.UTF-8
LC_CTYPE=ru_RU.UTF-8
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_ADMIN=
EMAIL_TIMEOUT=
EMAIL_USE_TLS=
```

### Сборка и запуск (миграции выполнятся автоматически)
```
docker-compose -f docker-compose.dev.yml up -d --build
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

### Запуск тестов

```
docker-compose -f docker-compose.dev.yml exec web python manage.py test --keepdb
```

### API

Документация: http://localhost:8000/redoc/

Для авторизации, нужно в заголовке передавать следующее:
```
Bearer {{access}}
```

## production-контейнер

### .env.prod
Создать файл .env.prod в папке проекта (aitarget_test_task) по шаблону.
Необходимо заполнить недостающие данные

```
DEBUG=0
ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
SECRET_KEY=secret-django-key
POSTGRES_DB=mylibrary
POSTGRES_USER=mylibrary_user
POSTGRES_PASSWORD=mylibrary_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE=postgres
LC_COLLATE=ru_RU.UTF-8
LC_CTYPE=ru_RU.UTF-8
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_ADMIN=
EMAIL_TIMEOUT=
EMAIL_USE_TLS=
```


## Собрать и запустить контейнер 

```
docker-compose up -d --build 
```

### Запуск миграций, сборка статики и созданию админа
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic
docker-compose exec web python manage.py createsuperuser
```

### API

Документация: http://localhost/redoc/

Для авторизации, нужно в заголовке передавать следующее:
```
Bearer {{access}}
```

