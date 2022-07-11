"""Configurações gerais da API da ANA."""

from pydantic import BaseModel


class ConfiguracoesANA(BaseModel):
    """Configurações gerais da API."""

    arg_plu: int = 2
    arg_flu: int = 1
    arg_telemetria: int = 1
    arg_convencional: int = 0
    arg_tele_e_convencionais: str = ""
    url_base: str = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx"


config = ConfiguracoesANA()
