"""Configurações gerais da API do INMET."""

from pydantic import BaseModel


class ConfiguracoesINMET(BaseModel):
    """Configurações gerais da API."""

    url_base: str = "https://apitempo.inmet.gov.br"
    arg_chuva: str = "CHUVA"
    arg_pressao: str = "PRESS_ATM_MED"
    arg_temp_max: str = "TEMP_MAX"
    arg_temp_med: str = "TEMP_MIN"
    arg_temp_min: str = "TEMP_MIN"
    arg_umid_med: str = "UMID_MED"
    arg_umid_min: str = "UMID_MIN"
    arg_vento_med: str = "VEL_VENTO_MED"


config = ConfiguracoesINMET()
