FROM python:3.12-slim
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y gcc && apt-get install -y default-libmysqlclient-dev
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt
RUN export DJANGO_SETTINGS_MODULE=drf_starter_template.settings
RUN python manage.py collectstatic --no-input
RUN python manage.py makemigrations
RUN python manage.py migrate
