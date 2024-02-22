FROM python:3.12.1-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.7.1
# Set the working directory inside the container
WORKDIR /app

# Copy the poetry.lock and pyproject.toml files to the working directory
COPY poetry.lock pyproject.toml ./

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Disable virtualenv creation
RUN poetry config virtualenvs.create false

# Install the required dependencies using Poetry
RUN poetry install --no-root --no-interaction

# Copy the rest of the application code to the working directory
COPY . .

# Specify the command to run when the container starts
CMD [ "python", "main.py" ]
