"""Configurações gerais do MERGE."""

from pydantic import BaseModel


class ConfiguracoesMERGE(BaseModel):
    """Configurações do MERGE."""

    url_base: str = "http://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM"
    threads: int = 20


config = ConfiguracoesMERGE()
