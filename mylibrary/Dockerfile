FROM python:3.7-slim

RUN mkdir /app
RUN mkdir /app/static
RUN mkdir /app/media

COPY ./requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . /app

WORKDIR /app

CMD ["gunicorn", "mylibrary.wsgi:application", "--bind", "0:8000" ]

