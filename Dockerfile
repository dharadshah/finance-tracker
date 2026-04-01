# Base image - official Python 3.11 slim version
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency files first (allows Docker to cache this layer)
COPY pyproject.toml poetry.lock ./

# Install poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy the rest of the project
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]