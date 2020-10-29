FROM python:latest
RUN mkdir /app
COPY ./src /app
COPY ./.env /app
COPY ./requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt