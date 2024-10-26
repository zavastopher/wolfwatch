FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . /app

EXPOSE 3001
CMD gunicorn -b 0.0.0.0:3001 -w 4 'server:create_app()'