import logging
import os

from aiocache import Cache
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import APIKeyHeader
from starlette import status

from app.db import database
from app.models import IPAddress
from app.service import TorIpService

logger = logging.getLogger(__name__)

app = FastAPI()

cache = Cache(Cache.MEMORY)
tor_ip_service = TorIpService(cache)


X_API_KEY = APIKeyHeader(name="X-API-Key")


def check_authentication_header(x_api_key: str = Depends(X_API_KEY)):
    """Validates API Key"""

    if x_api_key == os.getenv("TORLIST_API_KEY", "plzch4ng3m3"):
        return {}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post(
    "/whitelisted_ips",
    status_code=201,
    dependencies=[Depends(check_authentication_header)],
)
async def add_whitelist_ip(ip: IPAddress):
    ip_id = await tor_ip_service.save_whitelist_ip(ip)
    return {"id": ip_id}


@app.get("/ips", dependencies=[Depends(check_authentication_header)])
async def read_ips(filtered: bool = Query(False, description="If true, filter ips present in whitelist", )):
    ips = await tor_ip_service.get_ips()
    if filtered:
        whitelisted_ips = await tor_ip_service.get_whitelisted_ips()
        flattened_whitelisted_ips = [ip["ip"] for ip in whitelisted_ips]
        filtered_ips = [ip for ip in ips if ip not in flattened_whitelisted_ips]
        filtered_ips.sort()
        return {"ips": filtered_ips}
    else:
        ips.sort()
        return {"ips": ips}
