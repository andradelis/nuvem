"""Módulo para obtenção de dados do FTP do CPTEC."""

import queue
import threading
from pathlib import Path
from typing import Optional, Union

import geopandas as gpd
import pandas as pd
import requests
import timeless
import xarray as xr

from chuvisco import grade
from chuvisco.MERGE.config import config


class MERGE:
    def __init__(self) -> None:
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
        dir_dados: Optional[Path] = None,
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

        dir_dados : Path
            Diretório onde estão localizados os arquivos do MERGE. Caso nenhum diretório seja passado,
            os dados do MERGE serão baixados no diretório temporário passado para o parâmetro dir_tmp.

        dir_tmp : Path
            Diretório temporário onde será baixado o dataset do MERGE. O dataset é obtido através do
            download do dataset em um diretório e posterior abertura do dataset para retorno da função.

        Returns
        ----------
        Union[xr.Dataset, xr.DataArray, pd.DataFrame]
            Chuva do MERGE dentro do contorno.
        """
        if dir_dados:
            arquivos_merge = list(dir_dados.glob("*.grib2"))
        else:
            self.obter_dados_diarios(
                data_inicial=data_inicial, data_final=data_final, dir_tmp=dir_tmp
            )
            arquivos_merge = list(dir_tmp.glob("*.grib2"))

        ds = xr.open_mfdataset(
            arquivos_merge, concat_dim="valid_time", combine="nested", engine="cfgrib"
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
            dataset_recortado = dataset_recortado.drop(
                ["time", "step", "surface", "spatial_ref"]
            )
            df_merge = dataset_recortado.to_dataframe()
            df_merge.rename(columns={"prec": "merge"}, inplace=True)
            df_merge.index.name = "data"
            df_merge.index = df_merge.index.date
            df_merge = df_merge.sort_index()
            return df_merge

        return dataset_recortado


merge = MERGE()
