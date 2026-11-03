FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hours/ hours/
WORKDIR /app/hours
RUN python manage.py collectstatic --noinput

# ponytail: migrate on start; fine for one container, move to a one-off job if you ever run replicas
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn hours.wsgi -b 127.0.0.1:8000 -w 3 --timeout 300"]
