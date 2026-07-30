FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/opt/app-root/src

WORKDIR /opt/app-root/src

RUN groupadd -g 1001 app && useradd -u 1001 -g app -m app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=1001:1001 app ./app
COPY --chown=1001:1001 knowledge ./knowledge

USER 1001
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
