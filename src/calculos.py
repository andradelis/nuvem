import pandas as pd
import numpy as np

def mlt(serie: pd.Series) -> pd.Series:
    """
    Obtenção da média mensal de longo termo de uma série de dados.
    
    Parameters
    ----------
    serie : pd.Series
        Série de vazões do posto.
        
    Returns
    -------
    pd.Series
        Série de médias de vazão por mês do posto.    
    """
    return serie.groupby(serie.index.month).mean()

def curva_chave(cotas: pd.Series, vazoes: pd.Series, grau: int = 2) -> np.ndarray:
    """
    Determinação dos coeficientes da curva chave de um rio, a partir das séries de cotas e vazões.
    
    Parameters
    ----------
    cotas: pd.Series
        série de cotas do posto fluviométrico.
        
    vazoes: pd.Series
        série de vazões do posto fluviométrico.
        
    grau: int
        grau do polinômio de regressão.
    
    Returns
    -------
        (np.ndarray, np.ndarray): tupla contendo:
            1. array de valores no eixo y da função que melhor traduz a curva chave de um rio;
            2. coeficientes do polinômio de regressão.
    """
    x = np.array(cotas)
    y = np.array(vazoes)

    coefs = np.polyfit(x, y, 2)
    f = np.poly1d(coefs)

    polinomio = f(x)
    
    return polinomio, coefs
    