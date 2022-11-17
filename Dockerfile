FROM python:3.11-alpine
RUN pip install --no-cache-dir requests colorama
COPY . /app/

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
