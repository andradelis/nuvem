"""Módulo para obtenção de dados da Agência Nacional das Águas."""

import calendar
import xml.etree.ElementTree as ET

from typing import Union

import numpy as np
import pandas as pd
import requests


class ANA:
    """Classe de requisições da API da ANA."""

    url_base = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx"

    def __init__(self) -> None:
        """Inicialização da classe de consumo da API."""
        pass

    @classmethod
    def inventario(
        self,
        codigo: str = "",
        tipoest: Union[str, int] = "",
        telemetrica: Union[str, int] = 1,
    ) -> pd.DataFrame:
        """
        Obtém o inventário de postos da ANA.

        Obs: Caso nenhum parâmetro seja passado, será retornado o inventário completo.

        Parameters
        ----------
        codigo : str
            Código de 8 dígitos de um posto específico.

        tipoest : int
            Tipo de estação. (1: Fluviométrico; 2: Pluviométrico).

        telemetrica : bool
            1 caso seja desejado apenas telemétricas, 0 caso contrário. '' para obter
            todas.

        Returns
        -------
        pd.DataFrame
            Inventário de postos.
        """
        url_requisicao = f"{self.url_base}/HidroInventario?codEstDE={codigo}&codEstATE=&tpEst={tipoest}&nmEst=&nmRio=&codSubBacia=&codBacia=&nmMunicipio=&nmEstado=&sgResp=&sgOper=&telemetrica={telemetrica}"

        resposta = requests.get(url_requisicao)

        tree = ET.ElementTree(ET.fromstring(resposta.content))
        root = tree.getroot()

        estacoes = list()
        for estacao in root.iter("Table"):
            dados = {
                "latitude": [estacao.find("Latitude").text],
                "longitude": [estacao.find("Longitude").text],
                "altitude": [estacao.find("Altitude").text],
                "codigo": [estacao.find("Codigo").text],
                "nome": [estacao.find("Nome").text],
                "estado": [estacao.find("nmEstado").text],
                "municipio": [estacao.find("nmMunicipio").text],
                "responsavel": [estacao.find("ResponsavelSigla").text],
                "ultima_att": [estacao.find("UltimaAtualizacao").text],
                "tipo": [estacao.find("TipoEstacao").text],
                "data_ins": [estacao.find("DataIns").text],
                "data_alt": [estacao.find("DataAlt").text],
            }
            if telemetrica:
                dados.update(
                    {
                        "inicio_telemetria": [
                            estacao.find("PeriodoTelemetricaInicio").text
                        ],
                        "fim_telemetria": [estacao.find("PeriodoTelemetricaFim").text],
                    }
                )

            df = pd.DataFrame.from_dict(dados)
            df.set_index("codigo", inplace=True)
            estacoes.append(df)

        inventario = pd.concat(estacoes)

        return inventario

    def obter_chuva(
        self,
        cod_estacao: int,
        data_inicial: str = "",
        data_final: str = "",
        consistencia: int = 2,
    ) -> pd.DataFrame:
        """
        Obtém a série histórica de um posto pluviométrico.

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
        url_requisicao = f"{self.url_base}/HidroSerieHistorica?CodEstacao={cod_estacao}&dataInicio={data_inicial}&dataFim={data_final}&tipoDados=2&nivelConsistencia={consistencia}"
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
            df = pd.DataFrame({cod_estacao: dados}, index=datas)
            df_mes.append(df)

        try:
            serie = pd.concat(df_mes)
            serie.sort_index(inplace=True)
            serie[cod_estacao] = pd.to_numeric(serie[cod_estacao])
        except (ValueError):
            serie = pd.DataFrame([], columns=[cod_estacao])

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
