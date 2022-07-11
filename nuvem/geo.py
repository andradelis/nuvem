"""Módulo de funções referentes a utilidades geoespaciais."""
from typing import Any, List, Optional, Union

import geopandas as gpd
import pandas as pd
import shapely


def atribuir_geometrias(
    df: pd.DataFrame,
    xdim: str = "longitude",
    ydim: str = "latitude",
    crs: str = "EPSG:4326",
) -> gpd.geodataframe.GeoDataFrame:
    """
    Atribui uma coluna de geometrias ao dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe contendo uma coluna de latitude e outra de longitude.

    xdim : str
        Nome da coluna de longitude.

    ydim : str
        Nome da coluna de latitude.

    Returns
    -------
    gpd.geodataframe.GeoDataFrame
        Dataframe geoespacial contendo a coluna 'geometry',
        com as geometrias.
    """
    latitude = df[ydim]
    longitude = df[xdim]
    coordenadas = zipar_coordenadas(latitude=latitude, longitude=longitude)
    gdf = criar_geodataframe(df=df, coordenadas=coordenadas).set_crs(crs)

    return gdf


def dissolver(contorno: gpd.geodataframe.GeoDataFrame) -> gpd.geodataframe.GeoDataFrame:
    """
    Dissolve um geodataframe.

    Parameters
    -------
    contorno : gpd.geodataframe.GeoDataFrame
        Dataframe de coordenadas.

    Returns
    -------
    gpd.geodataframe.GeoDataFrame
        Dataframe de coordenadas.
    """
    crs = contorno.crs
    return contorno.dissolve().set_crs(crs=crs)


def obter_intersecao(
    contorno: gpd.geodataframe.GeoDataFrame, mascara: gpd.geodataframe.GeoDataFrame
) -> gpd.geodataframe.GeoDataFrame:
    """
    Obtém a porção do contorno de entrada que está dentro da máscara.

    Parameters
    -------
    contorno : gpd.geodataframe.GeoDataFrame
        Geodataframe do contorno de entrada.

    mascara : gpd.geodataframe.GeoDataFrame
        Geodataframe da máscara.

    Returns
    -------
    gpd.geodataframe.GeoDataFrame
        Porção do contorno de entrada dentro da máscara.
    """
    return gpd.overlay(contorno, mascara, how="intersection")


def converter_epsg(
    contorno: gpd.geodataframe.GeoDataFrame, epsg: int
) -> gpd.geodataframe.GeoDataFrame:
    """
    Converte um geodataframe para um outro sistema de coordenadas.

    Parameters
    -------
    contorno : gpd.geodataframe.GeoDataFrame
        Dataframe de coordenadas.

    epsg : int
        Código do sistema de coordenadas.

    Returns
    -------
    gpd.geodataframe.GeoDataFrame
        Dataframe de coordenadas.
    """
    return contorno.to_crs(epsg=epsg)


def obter_pontos_no_contorno(
    pontos: gpd.geodataframe.GeoDataFrame,
    contorno: gpd.geodataframe.GeoDataFrame,
) -> gpd.geodataframe.GeoDataFrame:
    """
    Obtém os pontos de um dataframe dentro de um contorno.

    Parameters
    ----------
    pontos : gpd.geodataframe.GeoDataFrame
        Série de geometrias dos pontos.

    contorno : gpd.geodataframe.GeoDataFrame
        Geometria do polígono de entrada.

    Returns
    -------
    gpd.geodataframe.GeoDataFrame
        Geodataframe de pontos dentro do contorno.
    """
    pontos_dentro = gpd.tools.sjoin(pontos, contorno, predicate="within", how="right")
    nome_index = pontos.index.name
    if nome_index:
        pontos_dentro.rename(columns={"index_left": nome_index}, inplace=True)
        pontos_dentro.set_index(nome_index, inplace=True)
    else:
        pontos_dentro.set_index("index_left", inplace=True)
    return pontos_dentro


def zipar_coordenadas(
    latitude: gpd.geoseries.GeoSeries, longitude: gpd.geoseries.GeoSeries
) -> List[shapely.geometry.Point]:
    """
    Concatena uma série de latitude e outra de longitude.

    A lista de saída contém objetos do tipo shapely.geometry.Point.

    Parameters
    -------
    latitude : gpd.geoseries.GeoSeries
        Série de latitudes.

    longitude : gpd.geoseries.Geoseries
        Série de longitudes

    Returns
    -------
    List[shapely.geometry.Point]
        Lista de coordenadas.
    """
    return [shapely.geometry.Point(x) for x in zip(longitude, latitude)]


def criar_geodataframe(
    coordenadas: List[Any], df: Optional[pd.DataFrame] = None
) -> gpd.geodataframe.GeoDataFrame:
    """
    Cria um geodataframe a partir de uma lista de coordenadas.

    Parameters
    -------
    coordenadas : List[Any]
        Lista de coordenadas.

    Returns
    -------
    gpd.geodataframe.GeoDataFrame
        Dataframe de coordenadas.
    """
    return gpd.GeoDataFrame(df, geometry=coordenadas)