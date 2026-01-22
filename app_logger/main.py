from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import asyncio
import uvicorn
from contextlib import asynccontextmanager

# Import de router
from router.logs_router import router

# Import servicio broker


# ===========================
# CONFIGURACIÓN FASTAPI
# ===========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Reemplazo de on_event(startup) con lifespan."""
    yield


app = FastAPI(
    title="Factory Data API",
    description="API REST para consultar datos de InfluxDB (solo admin)",
    version="1.0.0",
#    lifespan=lifespan
)


# ===========================
# CORS
# ===========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================
# REGISTRO DEL ROUTER /logs
# ===========================

app.include_router(router)


# ===========================
# EJECUCIÓN DIRECTA
# ===========================

if __name__ == "__main__":
    """
    Application entry point. Starts the Uvicorn server with SSL configuration.
    Runs the FastAPI application on host.
    """
    cert_file = os.getenv("SERVICE_CERT_FILE", "/certs/logger/logger-cert.pem")
    key_file = os.getenv("SERVICE_KEY_FILE", "/certs/logger/logger-key.pem")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("SERVICE_PORT", "6000")),
        reload=True,
        ssl_certfile=cert_file,
        ssl_keyfile=key_file,
    )
