import logging
import os

import fastapi

from samuel import apis
from samuel import types

app: fastapi.FastAPI = fastapi.FastAPI()


@app.get("/")
async def index():
    return fastapi.Response("Samuel is running")


@app.post("/api/generate_mask")
async def generate(request: types.GenerateMaskRequest) -> types.GenerateMaskResponse:
    try:
        return apis.generate_mask(request=request)
    except ValueError as e:
        raise fastapi.HTTPException(400, str(e))


# https://github.com/tiangolo/fastapi/issues/1508#issuecomment-638365277
@app.on_event("startup")
async def startup_event():
    uvicorn_logger = logging.getLogger("uvicorn")
    os.makedirs(os.path.expanduser("~/.cache/samuel/logs"), exist_ok=True)
    handler = logging.FileHandler(os.path.expanduser("~/.cache/samuel/samuel.log"))
    handler.setLevel(logging.DEBUG)
    fmt = "%(asctime)s [%(levelname)s] %(module)s:%(funcName)s:%(lineno)s - %(message)s"
    handler.setFormatter(logging.Formatter(fmt=fmt))
    uvicorn_logger.addHandler(handler)
