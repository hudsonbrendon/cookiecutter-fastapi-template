from pydantic import BaseModel


class Mensagem(BaseModel):
    msg: str
