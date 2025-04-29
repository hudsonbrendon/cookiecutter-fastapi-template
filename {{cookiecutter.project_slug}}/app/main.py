from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware

from app import schemas
from app.api.api_v1.api import api_router
from app.core.config import configuracoes

limitador = Limiter(
    key_func=get_remote_address,
    storage_uri=configuracoes.HOST_REDIS,
)


app = FastAPI(
    title=configuracoes.NOME_PROJETO,
    openapi_url=f"{configuracoes.API_V1_STR}/openapi.json",
)

app.state.limiter = limitador

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Definir todas as origens habilitadas para CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in configuracoes.ORIGENS_CORS_BACKEND],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)


@app.get("/atuador/saude", response_model=schemas.Mensagem)
def verificador_saude():
    return {"msg": "sucesso"}


app.include_router(api_router, prefix=configuracoes.API_V1_STR)
