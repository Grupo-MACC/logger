FROM python:3.12-slim-bookworm

# Configuration will be done as root
USER root

# Update pip, copy requirements file and install dependencies
RUN pip install --no-cache-dir --upgrade pip;
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# We will be working on this folder
WORKDIR /home/pyuser/code
ENV PYTHONPATH=/home/pyuser/code/app_logger
ENV RABBITMQ_USER=user
ENV RABBITMQ_PASSWORD=guest
ENV RABBITMQ_HOST=rabbitmq
ENV INFLUXDB_URL=http://10.1.12.50:5000
ENV INFLUXDB_TOKEN=MY_CUSTOM_TOKEN_123456
ENV INFLUXDB_ORG=my-org
ENV CONSUL_HOST=10.1.11.40
ENV CONSUL_PORT=8501

ENV SERVICE_PORT=6000
ENV SERVICE_CERT_FILE=/certs/logger/logger-cert.pem
ENV SERVICE_KEY_FILE=/certs/logger/logger-key.pem

# Create a non root user
RUN useradd -u 1000 -d /home/pyuser -m pyuser && \
    chown -R pyuser:pyuser /home/pyuser

# Copy the entrypoint script (executed when the container starts) and add execution permissions
COPY entrypoint.sh /home/pyuser/code/entrypoint.sh
RUN chmod +x /home/pyuser/code/entrypoint.sh

# Switch user so container is run as non-root user
USER 1000

# Copy the app to the container
COPY app_logger /home/pyuser/code/app_logger

# Run the application
ENTRYPOINT ["/home/pyuser/code/entrypoint.sh"]