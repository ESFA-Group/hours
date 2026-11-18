# BASE_IMAGE: point at a Docker Hub mirror if docker.io is unreachable from the build machine
ARG BASE_IMAGE=python:3.12-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hours/ hours/
WORKDIR /app/hours
RUN python manage.py collectstatic --noinput

# 0.0.0.0: nginx-proxy reaches the container over the shared "proxy" network
# ponytail: migrate on start; fine for one container, move to a one-off job if you ever run replicas
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn hours.wsgi -b 0.0.0.0:8000 -w 3 --timeout 300"]
