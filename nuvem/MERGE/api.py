"""Módulo para obtenção de dados do FTP do CPTEC."""

import queue
import threading

from pathlib import Path
from typing import Any
from typing import Mapping
from typing import Optional
from typing import Union

import geopandas as gpd
import pandas as pd
import requests
import timeless
import xarray as xr

from nuvem import grade
from nuvem.MERGE.config import config


class MERGE:
    """Classe de mapeamento de funções do MERGE."""

    def __init__(self) -> None:
        """Construtor da classe."""
        pass

    def baixar_dados_diarios(
        self,
        data_inicial: timeless.datetime,
        data_final: timeless.datetime,
        dir_tmp: Path = Path("/tmp/merge"),
    ) -> None:
        """
        Baixa arquivo do MERGE.

        Parameters
        ----------
        data_inicial: timeless.datetime
            Data inicial.

        data_final : timeless.datetime
            Data final.

        dir_tmp : Path
            Diretório temporário onde será baixado o dataset do MERGE. O dataset é obtido através do
            download do dataset em um diretório e posterior abertura do dataset para retorno da função.
        """

        def func(q, data):
            """Centro da função. É executada dentro das threads."""
            while True:
                data = q.get()
                try:
                    mes = str(data.month).zfill(2)
                    ano = str(data.year)
                    data_fmt = data.format("%Y%m%d")

                    nome_arquivo = f"MERGE_CPTEC_{data_fmt}.grib2"
                    arquivo_grib = dir_tmp.joinpath(nome_arquivo)

                    url = f"{config.url_base}/DAILY/{ano}/{mes}/{nome_arquivo}"
                    req = requests.get(url=url)

                    if req.status_code == 200:
                        with open(arquivo_grib, "wb") as f:
                            f.write(req.content)

                        print(f"Arquivo do dia {data.format('%d/%m/%Y')} ok")
                except Exception as e:
                    print(
                        f"Falha no download do arquivo do dia {data.format('%d/%m/%Y')}. Erro: {e}"
                    )

                q.task_done()

        dir_tmp.mkdir(exist_ok=True, parents=True)
        datas = timeless.period(start=data_inicial, end=data_final, freq="days")

        fila = queue.Queue()  # type: ignore

        for data in datas:
            fila.put(data)

        for _, data in zip(range(config.threads), datas):
            worker = threading.Thread(
                target=func,
                args=(fila, data),
                daemon=True,
            )
            worker.start()

        fila.join()

    def obter_chuva_no_contorno(
        self,
        data_inicial: timeless.datetime,
        data_final: timeless.datetime,
        contorno: gpd.geodataframe.GeoDataFrame,
        media_regional: bool = False,
        dados: Optional[Union[xr.Dataset, xr.DataArray]] = None,
        dir_tmp: Path = Path("/tmp/merge"),
    ) -> Union[xr.Dataset, xr.DataArray, pd.DataFrame]:
        """
        Obtém a chuva do MERGE dentro de um contorno.

        Parameters
        ----------
        data_inicial: timeless.datetime
            Data inicial.

        data_final : timeless.datetime
            Data final.

        contorno : gpd.geodataframe.GeoDataFrame
            Contorno de onde serão extraídos os dados de chuva.

        media_regional : bool
            Se é desejado que seja extraída a média regional do dataset. Caso True, é retornada a média
            de chuva na área, em formato de dataframe. Caso False, são retornados os dados em grade originais.

        dados : Optional[Union[xr.Dataset, xr.DataArray]]
            Dados do MERGE. Caso nenhum dataset seja passado, os dados do MERGE serão baixados no diretório
            temporário passado para o parâmetro dir_tmp.

        dir_tmp : Path
            Diretório temporário onde será baixado o dataset do MERGE. O dataset é obtido através do
            download do dataset em um diretório e posterior abertura do dataset para retorno da função.

        Returns
        -------
        Union[xr.Dataset, xr.DataArray, pd.DataFrame]
            Chuva do MERGE dentro do contorno.
        """
        if isinstance(dados, xr.Dataset) or isinstance(dados, xr.DataArray):
            ds = dados
        else:
            self.baixar_dados_diarios(
                data_inicial=data_inicial, data_final=data_final, dir_tmp=dir_tmp
            )
            arquivos_merge = list(dir_tmp.glob("*.grib2"))
            ds = xr.open_mfdataset(
                arquivos_merge,
                concat_dim="valid_time",
                combine="nested",
                engine="cfgrib",
            ).prec

        ds_lon_corrigida = grade.converter_longitude_para_limites_180(
            dataset=ds,
        )
        dataset_recortado = grade.recortar_dataset_no_contorno(
            dataset=ds_lon_corrigida, contorno=contorno
        )

        if media_regional:
            dataset_recortado = grade.media_regional(
                dataset=dataset_recortado,
            )
            variaveis_a_dropar: Optional[Mapping[Any, Any]] = [
                "time",
                "step",
                "surface",
                "spatial_ref",
            ]
            dataset_recortado = dataset_recortado.drop(variaveis_a_dropar)
            df_merge = dataset_recortado.to_dataframe()
            df_merge.rename(columns={"prec": "merge"}, inplace=True)
            df_merge.index.name = "data"
            df_merge.index = df_merge.index.date
            df_merge = df_merge.sort_index()
            return df_merge

        return dataset_recortado


merge = MERGE()
