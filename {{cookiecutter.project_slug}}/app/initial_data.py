import logging

from app.db.init_db import iniciar_db
from app.db.session import SessaoLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def iniciar() -> None:
    db = SessaoLocal()

    iniciar_db(db)


def principal() -> None:
    logger.info("Criando dados iniciais.")
    iniciar()
    logger.info("Dados iniciais criados.")


if __name__ == "__main__":
    principal()
