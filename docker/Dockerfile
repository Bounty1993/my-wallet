# Pull base image
FROM python:3.7-slim

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy project
COPY . /my_wallet/

# Set work directory
WORKDIR /my_wallet

# Install dependencies
RUN pip install -r /my_wallet/requirements/dev.txt

COPY ./docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]