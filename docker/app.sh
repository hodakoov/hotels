#!/bin/bash

# Функция проверки доступности базы данных
function wait_for_db() {
  until pg_isready -h db -p 5432 -U "$POSTGRES_USER"; do
    echo "Waiting for database..."
    sleep 2
  done
}

wait_for_db

alembic upgrade head

gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
