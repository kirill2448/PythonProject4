FROM python:3.11

WORKDIR /app
COPY . .



CMD ["flask", "run", "--host=127.0.0.1", "--port=5000"]
