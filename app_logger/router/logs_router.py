from fastapi import APIRouter, HTTPException, Query, Depends, Header
from influxdb_client import InfluxDBClient
from typing import Optional
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from consul_client import get_consul_client
import os
import logging
import asyncio
from sql import schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs/private", tags=["logs"])

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://10.1.12.50:5000")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN", "MY_CUSTOM_TOKEN_123456")
INFLUX_ORG = os.getenv("INFLUXDB_ORG", "my-org")

# Cache interno (simple)
# _influx_client: Optional[InfluxDBClient] = None
# _influx_query_api = None
# _influx_lock = asyncio.Lock()

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()


# async def _get_query_api():
#     """
#     Devuelve query_api inicializado una sola vez.

#     - Resuelve INFLUX_URL vía Consul solo la primera vez.
#     - Crea InfluxDBClient solo la primera vez.
#     - Reutiliza el mismo query_api en llamadas posteriores.
#     """
#     global INFLUX_URL, _influx_client, _influx_query_api

#     if _influx_query_api is not None:
#         return _influx_query_api

#     async with _influx_lock:
#         if _influx_query_api is not None:
#             return _influx_query_api

#         # Aquí sí puedes usar await (ya estás dentro de una async def)
#         INFLUX_URL = await get_consul_client().get_service_base_url("logs_inf")

#         _influx_client = InfluxDBClient(
#             url=INFLUX_URL,
#             token=INFLUX_TOKEN,
#             org=INFLUX_ORG,
#         )
#         _influx_query_api = _influx_client.query_api()
#         return _influx_query_api

@router.get("/")
async def root():
    return {
        "service": "Factory Data API",
        "version": "1.0.0",
        "note": "Todos los endpoints /logs requieren rol admin",
        "endpoints": {
            "errors": "/logs/errors",
            "monitoring": "/logs/monitoring",
            "debug": "/logs/debug",
            "health": "/health"
        }
    }

@router.get("/health", include_in_schema=False)
async def health() -> dict:
    """ Healthcheck LIVENESS (para Consul / balanceadores). """
    return {"detail": "OK"}


@router.get("/errors")
async def get_errors(
    start: str = Query("-1h"),
    stop: str = Query("now()"),
    limit: int = Query(100, ge=1, le=1000),
    service: Optional[str] = None,
    severity: Optional[str] = None
):
    try:
        filters = []
        if service:
            filters.append(f'|> filter(fn: (r) => r["service"] == "{service}")')
        if severity:
            filters.append(f'|> filter(fn: (r) => r["severity"] == "{severity}")')

        filter_str = "\n  ".join(filters)

        query = f'''
        from(bucket: "factory_errors")
          |> range(start: {start}, stop: {stop})
          |> filter(fn: (r) => r["_measurement"] == "logs")
          {filter_str}
          |> limit(n: {limit})
          |> sort(columns: ["_time"], desc: true)
        '''

        # query_api = await _get_query_api()
        result = query_api.query(query)

        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "time": record.get_time().isoformat(),
                    "service": record.values.get("service"),
                    "severity": record.values.get("severity"),
                    "field": record.get_field(),
                    "value": record.get_value()
                })

        return {
            "bucket": "factory_errors",
            "count": len(data),
            "filters": {"service": service, "severity": severity},
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {str(e)}")

@router.get("/monitoring")
async def get_monitoring(
    start: str = Query("-1h"),
    stop: str = Query("now()"),
    limit: int = Query(100, ge=1, le=1000),
    service: Optional[str] = None,
    severity: Optional[str] = None
):
    try:
        filters = []
        if service:
            filters.append(f'|> filter(fn: (r) => r["service"] == "{service}")')
        if severity:
            filters.append(f'|> filter(fn: (r) => r["severity"] == "{severity}")')

        filter_str = "\n  ".join(filters)

        query = f'''
        from(bucket: "factory_monitoring")
          |> range(start: {start}, stop: {stop})
          |> filter(fn: (r) => r["_measurement"] == "logs")
          {filter_str}
          |> limit(n: {limit})
          |> sort(columns: ["_time"], desc: true)
        '''

        # query_api = await _get_query_api()
        result = query_api.query(query)

        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "time": record.get_time().isoformat(),
                    "service": record.values.get("service"),
                    "severity": record.values.get("severity"),
                    "field": record.get_field(),
                    "value": record.get_value()
                })

        return {
            "bucket": "factory_monitoring",
            "count": len(data),
            "filters": {"service": service, "severity": severity},
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {str(e)}")

@router.get("/debug")
async def get_debug(
    start: str = Query("-1h"),
    stop: str = Query("now()"),
    limit: int = Query(100, ge=1, le=1000),
    service: Optional[str] = None
):
    try:
        service_filter = f'|> filter(fn: (r) => r["service"] == "{service}")' if service else ""

        query = f'''
        from(bucket: "factory_debug")
          |> range(start: {start}, stop: {stop})
          |> filter(fn: (r) => r["_measurement"] == "logs")
          {service_filter}
          |> limit(n: {limit})
          |> sort(columns: ["_time"], desc: true)
        '''

        # query_api = await _get_query_api()
        result = query_api.query(query)

        data = []
        for table in result:
            for record in table.records:
                data.append({
                    "time": record.get_time().isoformat(),
                    "service": record.values.get("service"),
                    "severity": record.values.get("severity"),
                    "field": record.get_field(),
                    "value": record.get_value()
                })

        return {
            "bucket": "factory_debug",
            "count": len(data),
            "filters": {"service": service},
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {str(e)}")
