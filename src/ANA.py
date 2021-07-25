import calendar
import numpy as np
import pandas as pd
import requests
import xml.etree.ElementTree as ET

class ANA:
    """Classe de requisições da API da ANA."""
    
    
    url_base = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx"
    
    
    def __init__(self) -> None:
        """Inicialização da classe de consumo da API."""
        pass
    
    
    def obter_serie_vazoes(self, cod_estacao: int, data_inicial: str = "", data_final: str = "") -> pd.DataFrame:
        """
        Obtenção da série histórica de um posto fluviométrico.
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
        print(f"URL da requisição: {url_requisicao}\nObtendo dados de vazão do posto {cod_estacao}...")
        resposta = requests.get(url_requisicao)   
        
        tree = ET.ElementTree(ET.fromstring(resposta.content))
        root = tree.getroot()
        
        df_mes = []
        for mes in root.iter('SerieHistorica'):
            consistencia = mes.find("NivelConsistencia").text
            maxima = mes.find("Maxima").text
            minima = mes.find("Minima").text
            media = mes.find("Media").text

            primeiro_dia_mes = pd.to_datetime(mes.find('DataHora').text, dayfirst=True)
            ultimo_dia_mes = calendar.monthrange(primeiro_dia_mes.year, primeiro_dia_mes.month)[1]
            lista_dias_mes = pd.date_range(primeiro_dia_mes, periods=ultimo_dia_mes, freq='D').tolist()

            dados, datas = [], []
            for i in range(len(lista_dias_mes)):
                datas.append(lista_dias_mes[i])
                dia = i + 1
                vazao = 'Vazao{:02}'.format(dia)
                dado = mes.find(vazao).text

                dados.append(dado)
            df = pd.DataFrame({'vazoes': dados}, index = datas)
            df = df.assign(
                maxima = maxima,
                minima = minima, 
                media = media,
                consistencia = consistencia,
            )
            df_mes.append(df)

        serie = pd.concat(df_mes)
        serie.sort_index(inplace = True)
        serie.vazoes = pd.to_numeric(serie.vazoes)
        
        return serie    
    
    
    def obter_cotas(self, cod_estacao: int, data_inicial: str = "", data_final: str = "") -> pd.DataFrame:
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
        print(f"URL da requisição: {url_requisicao}\nObtendo cotas do posto {cod_estacao}...")
        resposta = requests.get(url_requisicao)   
        
        tree = ET.ElementTree(ET.fromstring(resposta.content))
        root = tree.getroot()
        
        df_mes = []
        for mes in root.iter('SerieHistorica'):
            codigo = mes.find('EstacaoCodigo').text
            
            primeiro_dia_mes = pd.to_datetime(mes.find('DataHora').text, dayfirst=True)
            ultimo_dia_mes = calendar.monthrange(primeiro_dia_mes.year, primeiro_dia_mes.month)[1]
            lista_dias_mes = pd.date_range(primeiro_dia_mes, periods=ultimo_dia_mes, freq='D').tolist()

            dados, datas = [], []
            for i in range(len(lista_dias_mes)):
                datas.append(lista_dias_mes[i])
                dia = i + 1
                cota = 'Cota{:02}'.format(dia)
                try:
                    dado = mes.find(cota).text
                except AttributeError:
                    dado = np.nan
                dados.append(dado)
                
            df = pd.DataFrame({'cota': dados}, index = datas)
            df_mes.append(df)

        serie = pd.concat(df_mes)
        serie.sort_index(inplace = True)
        serie.index = pd.to_datetime(serie.index)
        serie.cota = pd.to_numeric(serie.cota)
        serie.cota = serie.cota/100
        
        return serie   