# образ на основе которого создаём контейнер
FROM python:3.7.11-alpine

# рабочая директория внутри проекта
WORKDIR /usr/src/aitarget_test_task/mylibrary/

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# устанавливаем зависимости
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# копируем содержимое текущей папки в контейнер
COPY . .

ENTRYPOINT ["/usr/src/aitarget_test_task/mylibrary/entrypoint.sh"]