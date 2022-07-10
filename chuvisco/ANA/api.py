"""Módulo para obtenção de dados da Agência Nacional das Águas."""

import calendar
import xml.etree.ElementTree as ET
from typing import Optional, Union

import numpy as np
import pandas as pd
import requests
import timeless

from chuvisco.ANA import utils
from chuvisco.ANA.config import config


class ANA:
    """Classe de requisições da API da ANA."""

    def __init__(self) -> None:
        """Inicialização da classe de consumo da API."""
        pass

    def inventario_plu(
        self,
        codigo: Union[str, int] = "",
        convencional: bool = True,
        telemetrica: bool = True,
    ) -> pd.DataFrame:
        """
        Obtém o inventário de postos pluviométricos da ANA.

        Obs: Caso nenhum parâmetro seja passado, será retornado o inventário completo.

        Parameters
        ----------
        codigo : Union[str, int]
            Código de 8 dígitos de um posto específico.

        telemetrica : bool
            Se o usuário deseja dados de postos telemétricos.

        convencional : bool
            Se o usuário deseja dados de postos convencionais.

        Returns
        -------
        pd.DataFrame
            Inventário de postos pluviométricos.
        """
        inventario = utils.obter_inventario(
            codigo=codigo,
            telemetrica=telemetrica,
            convencional=convencional,
            tipo_estacao=config.arg_plu,
        )

        for coordenada in ["latitude", "longitude"]:
            inventario[coordenada] = pd.to_numeric(inventario[coordenada])
        return inventario

    def inventario_flu(
        self,
        codigo: Union[str, int] = "",
        convencional: bool = True,
        telemetrica: bool = True,
    ) -> pd.DataFrame:
        """
        Obtém o inventário de postos fluviométricos da ANA.

        Obs: Caso nenhum parâmetro seja passado, será retornado o inventário completo.

        Parameters
        ----------
        codigo : Union[str, int]
            Código de 8 dígitos de um posto específico.

        telemetrica : bool
            Se o usuário deseja dados de postos telemétricos.

        convencional : bool
            Se o usuário deseja dados de postos convencionais.

        Returns
        -------
        pd.DataFrame
            Inventário de postos fluviométricos.
        """
        inventario = utils.obter_inventario(
            codigo=codigo,
            telemetrica=telemetrica,
            convencional=convencional,
            tipo_estacao=config.arg_flu,
        )

        for coordenada in ["latitude", "longitude"]:
            inventario[coordenada] = pd.to_numeric(inventario[coordenada])
        return inventario

    def obter_chuva(
        self,
        codigo: Union[str, int],
        data_inicial: Optional[timeless.datetime] = None,
        data_final: Optional[timeless.datetime] = None,
        consistido: bool = True,
    ) -> pd.DataFrame:
        """
        Obtém a série histórica de um posto pluviométrico.

        Caso não haja dados em algum intervalo do período solicitado, retorna todos os dados disponíveis.

        Parameters
        ----------
        codigo : Union[str, int]
            Código da estação fluviométrica.

        data_inicial : Optional[timeless.datetime]
            Data de início do intervalo.

        data_final : Optional[timeless.datetime]
            Data final do intervalo.

        consistido : bool
            Se a série de chuva está consistida.

        Returns
        -------
            pd.DataFrame: Dataframe contendo a série de vazões do posto, o nível máximo, médio e mínimo de cada mês e a consistência do dado (1: não consistido; 2: consistido)
        """
        consistencia = 2 if consistido else 1
        data_inicial_str = data_inicial.format("%d/%m/%Y")
        data_final_str = data_final.format("%d/%m/%Y")

        url_requisicao = (
            f"{config.url_base}/HidroSerieHistorica?CodEstacao={codigo}&"
            f"dataInicio={data_inicial_str}&dataFim={data_final_str}&tipoDados=2"
            f"&nivelConsistencia={consistencia}"
        )
        resposta = requests.get(url_requisicao)

        tree = ET.ElementTree(ET.fromstring(resposta.content))
        root = tree.getroot()

        df_mes = list()
        for mes in root.iter("SerieHistorica"):
            consistencia = mes.find("NivelConsistencia").text

            primeiro_dia_mes = pd.to_datetime(mes.find("DataHora").text, dayfirst=True)
            ultimo_dia_mes = calendar.monthrange(
                primeiro_dia_mes.year, primeiro_dia_mes.month
            )[1]
            lista_dias_mes = pd.date_range(
                primeiro_dia_mes, periods=ultimo_dia_mes, freq="D"
            ).tolist()

            dados, datas = [], []
            for i in range(len(lista_dias_mes)):
                datas.append(lista_dias_mes[i])
                dia = i + 1
                chuva = "Chuva{:02}".format(dia)
                dado = mes.find(chuva).text

                dados.append(dado)
            df = pd.DataFrame({codigo: dados}, index=datas)
            df_mes.append(df)

        try:
            serie = pd.concat(df_mes)
            serie.sort_index(inplace=True)
            serie[codigo] = pd.to_numeric(serie[codigo])
        except (ValueError):
            serie = pd.DataFrame([], columns=[codigo])

        return serie

    def obter_vazoes(
        self, cod_estacao: int, data_inicial: str = "", data_final: str = ""
    ) -> pd.DataFrame:
        """
        Obtém a série histórica de um posto fluviométrico.

        Caso não haja dados em algum intervalo do período solicitado, retorna todos os dados disponíveis.

        Parameters
        ----------
        cod_estacao : str
            Código da estação fluviométrica.

        data_inicial : str
            Data de início do intervalo, no formato dd/mm/yyyy.

        data_final : str
            Data final do intervalo, no formato dd/mm/yyyy.

        Returns
        -------
            pd.DataFrame: Dataframe contendo a série de vazões do posto, o nível máximo, médio e mínimo de cada mês e a consistência do dado (1: não consistido; 2: consistido)
        """

        url_requisicao = f"{self.url_base}/HidroSerieHistorica?CodEstacao={cod_estacao}&dataInicio={data_inicial}&dataFim={data_final}&tipoDados=3&nivelConsistencia="
        resposta = requests.get(url_requisicao)

        tree = ET.ElementTree(ET.fromstring(resposta.content))
        root = tree.getroot()

        df_mes = []
        for mes in root.iter("SerieHistorica"):
            consistencia = mes.find("NivelConsistencia").text
            maxima = mes.find("Maxima").text
            minima = mes.find("Minima").text
            media = mes.find("Media").text

            primeiro_dia_mes = pd.to_datetime(mes.find("DataHora").text, dayfirst=True)
            ultimo_dia_mes = calendar.monthrange(
                primeiro_dia_mes.year, primeiro_dia_mes.month
            )[1]
            lista_dias_mes = pd.date_range(
                primeiro_dia_mes, periods=ultimo_dia_mes, freq="D"
            ).tolist()

            dados, datas = [], []
            for i in range(len(lista_dias_mes)):
                datas.append(lista_dias_mes[i])
                dia = i + 1
                vazao = "Vazao{:02}".format(dia)
                dado = mes.find(vazao).text

                dados.append(dado)
            df = pd.DataFrame({"vazoes": dados}, index=datas)
            df = df.assign(
                maxima=maxima,
                minima=minima,
                media=media,
                consistencia=consistencia,
            )
            df_mes.append(df)

        serie = pd.concat(df_mes)
        serie.sort_index(inplace=True)
        serie.vazoes = pd.to_numeric(serie.vazoes)

        return serie

    def obter_cotas(
        self, cod_estacao: int, data_inicial: str = "", data_final: str = ""
    ) -> pd.DataFrame:
        """
        Obtenção da série de cotas de um posto fluviométrico.
        Caso não haja dados em algum intervalo do período solicitado, retorna todos os dados disponíveis.

        Parameters
        ----------
        cod_estacao : str
            Código da estação fluviométrica.

        data_inicial : str
            Data de início do intervalo, no formato dd/mm/yyyy.

        data_final : str
            Data final do intervalo, no formato dd/mm/yyyy.

        Returns
        -------
            pd.DataFrame: Dataframe contendo a série de cotas, em metros, do nível de água no posto fluviométrico analisado.
        """
        url_requisicao = f"{self.url_base}/HidroSerieHistorica?CodEstacao={cod_estacao}&dataInicio={data_inicial}&dataFim={data_final}&tipoDados=1&nivelConsistencia="
        resposta = requests.get(url_requisicao)

        tree = ET.ElementTree(ET.fromstring(resposta.content))
        root = tree.getroot()

        df_mes = []
        for mes in root.iter("SerieHistorica"):
            primeiro_dia_mes = pd.to_datetime(mes.find("DataHora").text, dayfirst=True)
            ultimo_dia_mes = calendar.monthrange(
                primeiro_dia_mes.year, primeiro_dia_mes.month
            )[1]
            lista_dias_mes = pd.date_range(
                primeiro_dia_mes, periods=ultimo_dia_mes, freq="D"
            ).tolist()

            dados, datas = [], []
            for i in range(len(lista_dias_mes)):
                datas.append(lista_dias_mes[i])
                dia = i + 1
                cota = "Cota{:02}".format(dia)
                try:
                    dado = mes.find(cota).text
                except AttributeError:
                    dado = np.nan
                dados.append(dado)

            df = pd.DataFrame({"cota": dados}, index=datas)
            df_mes.append(df)

        serie = pd.concat(df_mes)
        serie.sort_index(inplace=True)
        serie.index = pd.to_datetime(serie.index)
        serie.cota = pd.to_numeric(serie.cota)
        serie.cota = serie.cota / 100

        return serie


ana = ANA()
