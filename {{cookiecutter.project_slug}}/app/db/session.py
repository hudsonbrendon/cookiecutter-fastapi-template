from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import configuracoes

engine = create_engine(str(configuracoes.URI_BD_SQLALCHEMY), pool_pre_ping=True)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
