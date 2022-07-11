"""Funções de utilidade para tratamento de séries."""

import numpy as np
import pandas as pd


def percentil(serie: pd.Series, p: float) -> float:
    """
    Retorna o percentil de uma série.

    Parameters
    ----------
    serie : pd.Series
        Série de dados.

    p : float
        Percentil da série, de 0 a 1.

    Returns
    -------
    float
        Número da série que representa o percentil solicitado.
    """
    return serie.quantile(p)


def remover_outliers(serie: pd.Series, limite: float = 400) -> pd.Series:
    """
    Remove os valores maiores que o limite máximo possível da série.

    OBS: Onde houver outliers, o valor será substituído por NaN na série.

    Parameters
    ----------
    serie : pd.Series
        Série de dados.

    limite : float
        Limite máximo da série.

    Returns
    -------
    pd.Series
        Série sem outliers.
    """
    indice_outliers = serie[serie > limite].index
    serie.loc[indice_outliers] = np.nan

    return serie


def dropar_negativos(serie: pd.Series) -> pd.Series:
    """
    Substitui valores negativos da série por NaN.

    Parameters
    ----------
    serie : pd.Series
        Série de dados.

    Returns
    -------
    pd.Series
        Série com valores negativos substituídos por NaN.
    """
    serie_sem_na = serie.dropna()
    indices_negativos = serie_sem_na[serie_sem_na < 0].index
    serie.loc[indices_negativos] = np.nan
    return serie


def contabilizar_falhas(serie: pd.Series) -> float:
    """
    Contabiliza a porcentagem de falhas de uma série de dados.

    Parameters
    ----------
    serie : pd.Series
        Série de dados.

    Returns
    -------
    float
        Porcentagem de falhas na série.
    """
    n_dados = len(serie)
    n_nan = serie.isna().sum()

    return n_nan / n_dados
