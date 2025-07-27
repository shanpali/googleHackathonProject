# Use official Python image
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./
COPY . ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080

ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=8080
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["python", "app.py"]
