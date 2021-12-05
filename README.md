# aitarget_test_task
Тестовое задание для aitarget
Проект позволяет вести библиотеку книг авторов и организовывать 
подписки на них

# Подготовка к тестированию проекта
## Подготовить БД к работе
```
CREATE USER {DB_USER} 
    WITH PASSWORD {DB_PASSWORD};

ALTER ROLE {DB_USER} 
    SET client_encoding TO 'utf8';

ALTER ROLE {DB_USER} 
    SET default_transaction_isolation TO 'read committed';

ALTER ROLE {DB_USER} 
    SET timezone TO 'GMT+3';

CREATE DATABASE {DB_NAME} with 
    ENCODING='UTF-8' 
    LC_COLLATE='ru_RU.UTF-8' 
    LC_CTYPE='ru_RU.UTF-8';

CREATE DATABASE {DB_TEST_NAME} with 
    ENCODING='UTF-8' 
    LC_COLLATE='ru_RU.UTF-8' 
    LC_CTYPE='ru_RU.UTF-8';

GRANT ALL PRIVILEGES ON DATABASE 
    {DB_NAME}, {DB_TEST_NAME} to {DB_USER};  
```

## Склонировать и запустить проект

```
git clone git@github.com:cianoid/aitarget_test_task.git
cd aitarget_test_task
python3.7 -m venv venv
source venv/bin/activate
python manage.py migrate
```

## Запуск тестов

```
python manage.py test --keepdb
```

# Запуск проекта в Docker-контейенере

## .env
Создать .env-файл в папке проекта (aitarget_test_task) по шаблону

``` 
DEBUG=0
ALLOWED_HOSTS=localhost 127.0.0.1 [::1]
SECRET_KEY=
POSTGRES_DB_TEST=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_ADMIN=
EMAIL_TIMEOUT=60
EMAIL_USE_TLS=
DATABASE=postgres
LC_COLLATE=ru_RU.UTF-8
LC_CTYPE=ru_RU.UTF-8
```

## Собрать и запустить контейнер 

```
docker-compose up -d --build 
```
