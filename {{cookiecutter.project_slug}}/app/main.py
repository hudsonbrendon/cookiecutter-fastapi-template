from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from app.api.api_v1.api import api_router
from app.core.config import settings
from app import schemas

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_HOST,
)


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Definir todas as origens habilitadas para CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.get("/actuator/health", response_model=schemas.Msg)
def healthchecker():
    return {"msg": "success"}


app.include_router(api_router, prefix=settings.API_V1_STR)
