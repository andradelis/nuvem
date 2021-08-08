import pandas as pd
import numpy as np

def convolucao(chuva: List[float], vazoes:pd.DataFrame) -> pd.DataFrame:
    """
    Cálculo da resposta de uma bacia hidrográfica a um evento de chuva.

    O hidrograma resultante de um evento de chuva pode ser calculado a partir da 
    convolução aplicada ao hidrograma unitário de uma bacia hidrográfica.
    Considerando uma chuva efetiva formada por n blocos de duração D, ocorrendo em
    sequência, e uma bacia cujo hidrograma unitário para a chuva de duração D é
    dado por m ordenadas de duração D cada uma, a aplicação da convolução permite
    o cálculo da vazão Q em cada intervalo de tempo no ponto exutório da bacia.

    Example
    -------
    Dado o seguinte hidrograma unitário, relacionando intervalos de tempo a 
    suas respectivas vazões (m³/s/10mm), e a chuva efetiva em mm:


    $ tabela = {1:.5, 2: 2, 3: 4, 4: 7, 5: 5, 6: 3, 7: 1.8, 9: 1.5, 10: 1}
    $ hu = pd.DataFrame.from_dict(tabela, orient = 'index')
    $ chuva = [20, 25, 10]
    $ convolucao(chuva=chuva, vazoes=hu)


    O método retornará a resposta da bacia, calculada por convolução, em função da 
    chuva efetiva e do hidrograma unitário. A saída terá 11 intervalos de tempo, e
    a vazão máxima ocorrerá no quinto intervalo, atingindo 31.5 m³/s.

    Parameters
    ----------
    chuva : List[float]
    Blocos de precipitação efetiva.

    vazoes : pd.DataFrame
    Hidrograma unitário discreto.
    """
    multiplo = 10
    chuva_efetiva = [chuva / multiplo for chuva in chuvas]

    _vazoes = vazoes.iloc[:, 0].tolist()
    colunas = [pd.Series(data=np.nan, index=vazoes.index, name=_vazao) for _vazao in _vazoes]
    secao_vazoes = pd.concat(colunas, axis=1)

    inicio = 0
    for ix_vazao, vazao in enumerate(secao_vazoes.columns):
        for ix_chuva, chuva in enumerate(chuva_efetiva):
            try:
                secao_vazoes.iloc[inicio+ix_chuva, ix_vazao] = chuva_efetiva[ix_chuva]*vazao
            except IndexError:
                secao_vazoes = secao_vazoes.append(pd.Series(np.nan), ignore_index=True)
                secao_vazoes.iloc[inicio+ix_chuva, ix_vazao] = chuva_efetiva[ix_chuva]*vazao
        inicio += 1

    secao_vazoes.dropna(axis=1, how='all', inplace=True)
    secao_vazoes = secao_vazoes.assign(Q = secao_vazoes.sum(axis=1))
    secao_vazoes.insert(0, "chuva", pd.Series(chuva_efetiva))

    return secao_vazoes

def racional(C: float, i: float, A: float) -> float:
    """
    Cálculo da vazão superficial máxima através do método racional.
    
    O método racional baseia-se nas seguintes hipóteses:

    • Precipitação uniforme sobre toda a bacia.
    • Precipitação uniforme durante a duração da chuva.
    • A intensidade da chuva é constante.
    • O coeficiente de escoamento superficial é constante.
    • A vazão máxima ocorre quando toda a bacia está contribuindo (duração da chuva é igual ao tempo de concentração).
    • Aplicável em bacias pequenas (A ≤ 2 km2). Algunsautores recomendam o uso para bacias até 15 km2

    **Premissa do Método Racional** 
    A vazão é máxima quando a intensidade de chuva for máxima.
    Ou seja, quando toda a bacia estiver contribuindo para o escoamento, duração da chuva for igual ao tempo de concentração.

    Parameters
    ----------
    C : float
        Coeficiente de deflúvio.

    i : float
        Intensidade de chuva (mm/h) referente ao tempo de concentração (tc).

    A : float
        Área da bacia, em km²

    Returns
    --------
    float
        Vazão superficial máxima, em m³/s.
    """
    return 0.278*C*i*A

def solidos(c: float, serie: pd.Series) -> float:
    """
    Cálculo da vazão de sólidos em suspensão.
    
    Parameters
    ----------
    c : float
        Concentração de sólidos em suspensão média (mg/L).
    
    serie : pd.Series
        Série de vazões do posto (m³/s).
        
    Returns
    -------
    float
        Valor da vazão de sólidos em suspensão (ton/dia).
    """
    mlt = serie.mean()
    return 0.0864*mlt*c

def mlt(serie: pd.Series) -> pd.Series:
    """
    Obtenção da média mensal de longo termo de uma série de dados.
    
    Parameters
    ----------
    serie : pd.Series
        Série de vazões do posto (m³/s).
        
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
    