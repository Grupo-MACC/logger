from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import asyncio
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6000)
