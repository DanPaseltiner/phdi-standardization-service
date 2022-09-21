FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

EXPOSE 8080
CMD uvicorn main:api --host 0.0.0.0 --port 8080