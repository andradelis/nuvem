# nuvem

![texto](https://img.shields.io/static/v1?label=linguagem&message=python&color=green&style=flat-square "linguagem")

1. [Descrição](#descrição)  
2. [Funcionalidades](#funcionalidades)  
3. [Pré-requisitos](#pré-requisitos)  
4. [Como instalar](#como-instalar)
4. [Execução](#execucao)


## :scroll: Descrição

Repositório em constante construção destinado a compartilhar aprendizados na área de hidrologia. Os métodos encontrados nos módulos disponíveis neste repositório são ferramentas que utilizo em meus estudos. Sinta-se livre para contribuir! :)


## :sparkles: Funcionalidades

:heavy_check_mark: Consumo da API da ANA: obtenção de cotas e séries de vazão de um posto fluviométrico

:heavy_check_mark: Hidrograma de cheias por convolução

:heavy_check_mark: Determinação da curva chave

:heavy_check_mark: Cálculos hidrológicos básicos: fator de forma, coeficiente de runoff...

## :warning: Pré-requisitos

- [Python](https://www.python.org/) (obrigatório)

## :cd: Como instalar

```bash
# 1. no terminal, clone o projeto
git clone git@github.com:andradelis/nuvem.git

# 2. entre na pasta do projeto
cd nuvem

# 3. instale as dependências
pip install -r requirements.txt
```

## :arrow_forward: Execução

### MERGE - CPTEC/INPE

```python
import timeless
import geopandas as gpd
from nuvem.MERGE.api import merge

data_inicial = timeless.datetime(2022, 1, 1)
data_final = timeless.today()
contorno = gpd.read_file(
    <caminho-para-o-shapefile>
)

# obter chuva de satélite em uma área
df_merge = merge.obter_chuva_no_contorno(
    data_inicial=data_inicial,
    data_final=data_final,
    contorno=contorno,
    media_regional=True
)

# baixar dados diários do merge em disco
merge.baixar_dados_diarios(
    data_inicial=data_inicial,
    data_final=data_final
)

# também é possível utilizar o dataset baixado para obter a chuva no contorno
merge.obter_chuva_no_contorno(
    contorno=contorno,
    media_regional=True,
    dados=<caminho-para-o-dataset-gravado-em-disco>
)

```
### ANA

```python
from nuvem.ANA.api import ana
import timeless
import geopandas as gpd

# obtém o inventário de postos pluviométricos da ANA
inventario_ana_plu = ana.inventario_plu()

# obtém o inventário de postos fluviométricos da ANA
inventario_ana_flu = ana.inventario_flu()

# obtém a série de vazões e cotas de um posto fluviométrico
posto = 58235100
serie = ana.obter_vazoes(posto)
cotas = ana.obter_cotas(posto)

# obtém as séries de chuva dos postos dentro de um contorno
data_inicial = timeless.datetime(2022, 1, 1)
data_final = timeless.today()
contorno = gpd.read_file(
    <caminho-para-o-shapefile>
)
df_ana = ana.obter_chuva_no_contorno(
    data_final=data_final,
    data_inicial=data_inicial,
    contorno=contorno,
    telemetrica=True,
    convencional=False
)
```

### INMET
```python
from nuvem.INMET.api import inmet
import timeless
import geopandas as gpd

# obtém o inventário de estações telemétricas
inventario_telemetrica = inmet.inventario(telemetrica=True)
# obtém o inventário de estações convencionais
inventario_convencional = inmet.inventario(telemetrica=False)

# obtém dados medidos de uma estação em um período
data_inicial = timeless.datetime(2022, 1, 1)
data_final = timeless.today()

dados = inmet.obter_dados(
    data_inicial=data_inicial,
    data_final=data_final,
    codigo=A706,
    freq="D"
)

# obtém um mapeamento das variáveis disponíveis no 
# dataframe de medições do INMET
variaveis = inmet.variaveis()

# seleciona a variável de pressão
pressao_inmet = dados[variaveis['pressão']]

# obtém as séries de chuva dos postos dentro de um contorno
contorno = gpd.read_file(
    <caminho-para-o-shapefile>
)
df_inmet = inmet.obter_chuva_no_contorno(
    data_final=data_final,
    data_inicial=data_inicial,
    contorno=contorno,
)
```
### Cálculo da curva chave de um rio
![alt text](https://github.com/andradelis/hidro-os/blob/main/exemplos/curva_chave.png?raw=true)


### Estatísticas gerais de uma série
![alt text](https://github.com/andradelis/hidro-os/blob/main/exemplos/serie_mlt.png?raw=true)


### Hidrograma de cheias
![alt text](https://github.com/andradelis/hidro-os/blob/main/exemplos/hidrograma.png?raw=true)

