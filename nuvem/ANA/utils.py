"""Módulo de utilidades para manipulação e obtenção de dados da API da ANA."""

import xml.etree.ElementTree as ET

from typing import Union

import pandas as pd
import requests

from nuvem.ANA.config import config


def obter_tipo_medicao(
    telemetrica: bool,
    convencional: bool,
) -> Union[str, int]:
    """
    Define o argumento a ser enviado para a API.

    A API da ANA recebe 3 tipos possíveis de argumento para a requisição
    de dados quanto à medição:
        1: dados de postos telemétricos;
        0: dados de postos convencionais;
        '': dados de ambos os tipos de postos, representado por uma string
        vazia.

    Parameters
    ----------
    telemetrica : bool
        Se o usuário deseja obter dados de postos telemétricos.

    convencional : bool
        Se o usuário deseja obter dados de postos convencionais.

    Returns
    -------
    Union[str, int]
        Argumento de tipo de medição a ser passado para a API da ANA.
    """
    medicao: Union[str, int] = ""
    if telemetrica and convencional:
        medicao = config.arg_tele_e_convencionais
    elif telemetrica and not convencional:
        medicao = config.arg_telemetria
    elif not telemetrica and convencional:
        medicao = config.arg_convencional

    return medicao


def processar_inventario(
    root: ET.Element,
) -> pd.DataFrame:
    """
    Função de comodidade para processamento do inventário da ANA.

    Parameters
    ----------
    root : ET.Element
        Objeto xml obtido da API da ANA.

    Returns
    -------
    pd.DataFrame
        Dataframe contendo o inventário da ANA.
    """
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
            "inicio_telemetria": [estacao.find("PeriodoTelemetricaInicio").text],
            "fim_telemetria": [estacao.find("PeriodoTelemetricaFim").text],
        }

        df = pd.DataFrame.from_dict(dados)
        df.set_index("codigo", inplace=True)
        estacoes.append(df)

    return pd.concat(estacoes)


def obter_inventario(
    telemetrica: bool,
    convencional: bool,
    tipo_estacao: Union[str, int],
    codigo: Union[str, int],
) -> pd.DataFrame:
    """
    Obtém o inventário de um posto pluviométrico ou fluviométrico.

    Parameters
    ----------
    codigo : str
        Código de 8 dígitos de um posto específico.

    telemetrica : bool
        Se o usuário deseja dados de postos telemétricos.

    convencional : bool
        Se o usuário deseja dados de postos convencionais.

    tipo_estacao : Union[str, int]
        Tipo de estação, pluviométrica ou fluviométrica.

    Returns
    -------
    pd.DataFrame
        Inventário de postos pluviométricos.
    """
    medicao = obter_tipo_medicao(telemetrica=telemetrica, convencional=convencional)

    url_requisicao = (
        f"{config.url_base}/HidroInventario?codEstDE={codigo}&codEstATE=&tpEst={tipo_estacao}"
        f"&nmEst=&nmRio=&codSubBacia=&codBacia=&nmMunicipio=&nmEstado=&sgResp=&sgOper=&"
        f"telemetrica={medicao}"
    )

    resposta = requests.get(url_requisicao)

    tree = ET.ElementTree(ET.fromstring(resposta.content))
    root = tree.getroot()

    inventario = processar_inventario(
        root=root,
    )

    return inventario
