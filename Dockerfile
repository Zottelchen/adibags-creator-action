FROM python:3.11-alpine
# 3.11 is required for tomllib :)

# Install Poetry & dependencies
RUN curl -sSL https://install.python-poetry.org | python3 -
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install

# Copy the rest of the code
COPY . /app/

ENTRYPOINT ["/app/entrypoint.sh"]
