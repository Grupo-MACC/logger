#!/bin/bash

echo "Service: ${SERVICE_NAME}"

# Obtener la IP del contenedor
IP=$(hostname -i)
export IP
echo "IP: ${IP}"

# Función para terminar Uvicorn de forma limpia
terminate() {
  echo "Termination signal received, shutting down..."
  kill -SIGTERM "$UVICORN_PID"
  wait "$UVICORN_PID"
  echo "Uvicorn has been terminated"
}

trap terminate SIGTERM SIGINT

echo "Starting Uvicorn..."

# Arrancar Uvicorn apuntando al módulo correcto
uvicorn app_logger.main:app \
  --host 0.0.0.0 \
  --port 6000 &

UVICORN_PID=$!

wait "$UVICORN_PID"
