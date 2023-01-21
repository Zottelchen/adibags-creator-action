FROM python:3.11-alpine
# 3.11 is required for tomllib :)

# Configure Poetry
ENV POETRY_VERSION=1.2.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
RUN ls -al /opt
# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app
# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install

# Copy the rest of the code
COPY . /app/

RUN chmod -R 777 /app
RUN chmod +x /app/entrypoint.sh && chmod +x /app/create.py

# Run the app
ENTRYPOINT ["/app/entrypoint.sh"]
