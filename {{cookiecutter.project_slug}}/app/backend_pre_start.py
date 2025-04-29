import logging

from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.db.session import SessaoLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tentativas = 60 * 5  # 5 minutos
segundos_espera = 1


@retry(
    stop=stop_after_attempt(max_tentativas),
    wait=wait_fixed(segundos_espera),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def iniciar() -> None:
    try:
        db = SessaoLocal()
        # Tente criar uma sessão para verificar se o banco de dados está ativo
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(e)
        raise e


def principal() -> None:
    logger.info("Inicializando serviço...")
    iniciar()
    logger.info("Inicialização do serviço concluída.")


if __name__ == "__main__":
    principal()
