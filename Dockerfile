FROM python:3.12

RUN pip install --upgrade pip \
    && pip install poetry \ 
    && pip install uvicorn

WORKDIR /hashwatch

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY . .

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
