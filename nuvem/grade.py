"""Métodos utilitários para lidar com dados em grade."""

from typing import Union

import geopandas as gpd
import rioxarray
import xarray as xr


def converter_longitude_para_limites_180(
    dataset: Union[xr.Dataset, xr.DataArray],
    crs="epsg:4326",
    xdim="longitude",
    ydim="latitude",
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Converte a longitude de um dataset de 0 a 360 para -180 a 180.

    Parameters
    ----------
    dataset: Union[xr.Dataset, xr.DataArray]
        Dataset a ser ajustado.

    crs: str
        Sistema de coordenadas a ser utilizado.

    xdim: str
        Nome da dimensão x.

    ydim: str
        Nome da dimensão y.

    Returns
    --------
    Union[xr.Dataset, xr.DataArray]
        Dataset com a dimensão de longitude alterada.
    """
    dataset = dataset.assign_coords(
        longitude=(((dataset.longitude + 180) % 360) - 180)
    ).sortby(xdim)
    dataset = dataset.rio.set_spatial_dims(x_dim=xdim, y_dim=ydim)
    dataset = dataset.rio.write_crs(crs)
    return dataset


def recortar_dataset_no_contorno(
    dataset: Union[xr.Dataset, xr.DataArray],
    contorno: gpd.geodataframe.GeoDataFrame,
    crs: str = "EPSG:4326",
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Recorta o dataset de acordo com o polígono do contorno.

    Parameters
    ----------
    dataset: Union[xr.Dataset, xr.DataArray]
        Dataset a ser recortado.

    contorno: gpd.geodataframe.GeoDataFrame
        Molde do recorte.

    crs : str
        Referencial de coordenadas em EPSG.

    Returns
    -------
    Union[xr.Dataset, xr.DataArray]
        Dataset recortado de acordo com o molde do polígono do contorno.
    """
    return dataset.rio.clip(contorno["geometry"], crs)


def media_regional(
    dataset: Union[xr.Dataset, xr.DataArray],
    xdim: str = "longitude",
    ydim: str = "latitude",
) -> Union[xr.Dataset, xr.DataArray]:
    """
    Obtém a média regional de um dataset.

    Parameters
    ----------
    dataset : Union[xr.Dataset, xr.DataArray]
        Dataset a ser extraída a média regional.

    xdim : str
        Nome da dimensão x.

    ydim : str
        Nome da dimensão y.

    Returns
    -------
    Union[xr.Dataset, xr.DataArray]
        Média regional do dataset.
    """
    return dataset.mean(dim=[xdim, ydim])
