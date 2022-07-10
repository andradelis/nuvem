"""Módulo para obtenção de dados do Instituto Nacional de Meteorologia."""

from typing import Dict, List

import pandas as pd
import requests
import timeless

from chuvisco.INMET.config import config

# Código baseado no manual de uso da API de estações e dados meteorológicos do INMET: https://portal.inmet.gov.br/manual/manual-de-uso-da-api-estações


class INMET:
    """Classe de requisição da API do INMET."""

    def __init__(self) -> None:
        """Inicialização da classe de consumo da API."""
        pass

    @property
    def variaveis(self) -> Dict[str, str]:
        """
        Mapeamento de variáveis disponibilizadas pela API.
        
        As variáveis podem ser utilizadas para que sejam escolhidas no
        dataframe de dados de uma estação específica.
        """
        return {
            "chuva": config.arg_chuva,
            "pressão": config.arg_pressao,
            "temperatura máxima": config.arg_temp_max,
            "temperatura mínima": config.arg_temp_min,
            "temperatura média": config.arg_temp_med,
            "umidade mínima": config.arg_umid_min,
            "umidade média": config.arg_umid_med,
            "velocidade média do vento": config.vento_med 
        }

    def inventario(self, telemetrica: bool = True) -> pd.DataFrame:
        """
        Obtém todas as estações de acordo com o tipo de medição.

        Parameters
        ----------
        telemetrica : bool
            Se a medição é por telemetria. Caso False, retorna
            estações convencionais.

        Returns
        -------
        pd.DataFrame
            Estações disponíveis no inventário do INMET.
        """
        tipo = "T" if telemetrica else "M"
        url_requisicao = f"{config.url_base}/estacoes/{tipo}"
        resposta = requests.get(url_requisicao)
        df = pd.DataFrame(resposta.json())
        df.rename(
            columns={
                "VL_LATITUDE": "latitude",
                "VL_LONGITUDE": "longitude",
                "CD_ESTACAO": "codigo",
            },
            inplace=True,
        )
        df.set_index("codigo", inplace=True)

        return df

    def obter_dados(
        self,
        data_inicial: timeless.datetime,
        data_final: timeless.datetime,
        codigo: str,
        freq: str = "H",
    ) -> List[Dict[str, str]]:
        """
        Obtenção de dados horários ou diários referentes a uma estação automática ou manual específica.

        Parameters
        ----------
        data_inicial : timeless.datetime
            Data de início do intervalo no formato AAAA-MM-DD.

        data_final : timeless.datetime
            Data final do intervalo no formato AAAA-MM-DD.

        codigo : str
            Código da estação.

        freq : str
            Frequência dos dados. Pode ser H ou D, onde H se refere a dados horários e D, diários.

        Returns
        -------
            List[Dict[str, str]] : dados horários referentes a uma estação automática ou manual.
        """
        data_inicial_str = data_inicial.format("%Y-%m-%d")
        data_final_str = data_final.format("%Y-%m-%d")
        freq_ = "" if freq == "H" else "diaria/"

        url_requisicao = f"{config.url_base}/estacao/{freq_}{data_inicial_str}/{data_final_str}/{codigo}"
        resposta = requests.get(url_requisicao)
        df = pd.DataFrame(resposta.json())
        df.rename(
            columns={
                "VL_LATITUDE": "latitude",
                "VL_LONGITUDE": "longitude",
                "CD_ESTACAO": "codigo",
            },
            inplace=True,
        )
        df.set_index("codigo", inplace=True)

        return df


inmet = INMET()
