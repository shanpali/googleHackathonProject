# Use official Python image
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./
COPY . ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
