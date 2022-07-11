"""Módulo para obtenção de dados do Instituto Nacional de Meteorologia."""

import math

from typing import Dict
from typing import Optional

import geopandas as gpd
import pandas as pd
import requests
import timeless

from nuvem import geo
from nuvem.INMET.config import config


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
            "velocidade média do vento": config.arg_vento_med,
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
                "DT_MEDICAO": "data",
            },
            inplace=True,
        )
        df.set_index("codigo", inplace=True)
        for coordenada in ["latitude", "longitude"]:
            df[coordenada] = pd.to_numeric(df[coordenada])

        return df

    def obter_dados(
        self,
        data_inicial: timeless.datetime,
        data_final: timeless.datetime,
        codigo: str,
        freq: str = "H",
    ) -> pd.DataFrame:
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
        pd.DataFrame
            Dados referentes a uma estação automática ou manual.
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
                "DT_MEDICAO": "data",
            },
            inplace=True,
        )
        for coordenada in ["latitude", "longitude"]:
            df[coordenada] = pd.to_numeric(df[coordenada])

        df.set_index("data", inplace=True)
        df.index = pd.to_datetime(df.index)

        return df

    def obter_chuva(
        self,
        data_inicial: timeless.datetime,
        data_final: timeless.datetime,
        codigo: str,
        freq: str = "H",
    ) -> pd.DataFrame:
        """
        Obtenção de dados de chuva referentes a uma estação automática ou manual específica.

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
        pd.DataFrame
            Dados de chuva.
        """
        df = self.obter_dados(
            data_inicial=data_inicial,
            data_final=data_final,
            codigo=codigo,
            freq=freq,
        )

        df.rename(columns={config.arg_chuva: codigo}, inplace=True)
        return df[codigo]

    def obter_chuva_no_contorno(
        self,
        data_inicial: timeless.datetime,
        data_final: timeless.datetime,
        contorno: gpd.geodataframe.GeoDataFrame,
        telemetrica: bool = True,
        convencional: bool = True,
        freq: str = "D",
        inventario_plu: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Obtém as séries de chuva dentro de um contorno.

        Parameters
        ----------
        data_inicial : timeless.datetime
            Data inicial da série.

        data_final : timeless.datetime
            Data final da série.

        contorno : gpd.geodataframe.GeoDataFrame
            Contorno de onde serão extraídos os postos pluviométricos.

        telemetrica : bool
            Se as estações são telemétricas. Caso telemetrica=True e convencional=True,
            todas as estações serão retornadas.

        convencional : bool
            Se as estações são convencionais. Caso telemetrica=True e convencional=True,
            todas as estações serão retornadas.

        freq : str
            Frequência dos dados. Pode ser H ou D, onde H se refere a dados horários e D, diários.

        inventario_plu : Optional[pd.DataFrame]
            Diretório para o inventário de postos pluviométricos. Caso None, será obtido
            o inventário de forma programática e efêmera, sem ser alocado em disco. O
            inventário é necessário para a obtenção das coordenadas de todos os postos
            disponíveis. Reitera-se que o inventário plu deve possuir, como index, o código
            do posto ,e as colunas 'latitude' e 'longitude' para o funcionamento correto do
            método. Passar o inventário como argumento também faz com que sejam ignorados
            os argumentos passados para os parametros telemetria e convencional, uma vez que
            não é possível inferir de antemão a formatação do inventário local.

        Returns
        -------
        pd.DataFrame
            Séries de chuva dentro do contorno.
        """
        if isinstance(inventario_plu, pd.DataFrame):
            inventario_inmet = inventario_plu
        else:
            if telemetrica and convencional:
                inventario_telemetricas_inmet = self.inventario(telemetrica=True)
                inventario_convencionais_inmet = self.inventario(telemetrica=False)
                inventario_inmet = pd.concat(
                    [inventario_convencionais_inmet, inventario_telemetricas_inmet],
                    axis=0,
                )
            elif telemetrica and not convencional:
                inventario_inmet = self.inventario(telemetrica=True)
            elif not telemetrica and convencional:
                inventario_inmet = self.inventario(telemetrica=False)

        postos_inmet = inventario_inmet[["latitude", "longitude"]]
        gdf_plu = geo.atribuir_geometrias(df=postos_inmet)

        selecao_postos = geo.obter_pontos_no_contorno(pontos=gdf_plu, contorno=contorno)

        # obtém a série de chuva pra cada um dos postos
        # ? o INMET possui um limite de 1 ano de dados por requisição.
        # ? Logo, será feita a iteração por todos os anos desde o ano inicial
        # ? até o ano atual.
        quantidade_de_anos = math.ceil((data_final - data_inicial).days / 360)

        lista_chuva_postos = list()
        for posto in selecao_postos.index:
            data_inicial_apoio = data_inicial

            lista_chuva_anos = list()
            for _ in range(1, quantidade_de_anos + 1):
                data_final_apoio = data_inicial_apoio.add(years=1)

                chuva_ano = self.obter_chuva(
                    codigo=posto,
                    data_inicial=data_inicial_apoio,
                    data_final=data_final_apoio,
                    freq=freq,
                )
                lista_chuva_anos.append(chuva_ano)
                data_inicial_apoio = data_final_apoio

            chuva_posto = pd.concat(lista_chuva_anos, axis=0)
            # ! Algumas datas repetidas. Investigar.
            chuva_posto = chuva_posto.loc[~chuva_posto.index.duplicated(keep="first")]
            lista_chuva_postos.append(chuva_posto)

        return pd.concat(lista_chuva_postos, axis=1)


inmet = INMET()
