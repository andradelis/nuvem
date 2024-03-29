# nuvem

![texto](https://img.shields.io/static/v1?label=linguagem&message=python&color=green&style=flat-square "linguagem")

1. [Descrição](#descrição)  
2. [Funcionalidades](#funcionalidades)  
3. [Pré-requisitos](#pré-requisitos)  
4. [Como instalar](#como-instalar)
4. [Execução](#execucao)


## :scroll: Descrição

Wrapper user-friendly para facilitar o acesso aos dados hidrometeorológicos de grandes centros.
O `nuvem` conta com diversas funções para obtenção e manipulação de dados em grade e séries temporais.
Contribuições são bem vindas!

Aqui você vai encontrar:

:sparkles: Módulos para obtenção de dados de grandes centros!

1. API da ANA;

2. API do INMET;

3. FTP do CPTEC para dados do MERGE.

:sparkles: Diversos cálculos hidrológicos
   
   1. Hidrograma de cheias por convolução;
   
   2. Determinação da curva chave;
   
   3. Fator de forma;
   
   4. Coeficiente de runoff;
   
   5. etc...

:sparkles: Módulos de utilidade para lidar com dados em grade e séries temporais.

## :cd: Como instalar

```bash
# 1. no terminal, clone o projeto
git clone git@github.com:andradelis/nuvem.git

# 2. entre na pasta do projeto
cd nuvem

# 3. instale as dependências
bash conda-install.bash

# 4. Ative o ambiente do projeto!
conda activate nuvem
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

# baixar dados diários do merge em disco
merge.baixar_dados_diarios(
    data_inicial=data_inicial,
    data_final=data_final
)

# utilizar o dataset baixado para obter a chuva no contorno
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

# obtém os postos de chuva que estão localizados dentro de um contorno
contorno = gpd.read_file(
    <caminho-para-o-shapefile>
)
postos_ana = inventario_ana_plu[["latitude", "longitude"]]
gdf_plu = geo.atribuir_geometrias(df=postos_ana)
postos = geo.obter_pontos_no_contorno(pontos=gdf_plu, contorno=contorno)

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

