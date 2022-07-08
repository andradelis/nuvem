# chuvisco

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
git clone git@github.com:andradelis/chuvisco.git

# 2. entre na pasta do projeto
cd chuvisco

# 3. instale as dependências
pip install -r requirements.txt
```

## :arrow_forward: Execução
### Acesso aos dados disponibilizados na API da Agência Nacional das Águas.

```python
# importação da biblioteca
from chuvisco.ANA import ANA

# posto fluviométrico Queluz
posto = 58235100

# inicialização da classe para o uso dos métodos
ana_ = ANA()

# obtenção da série histórica de vazões do posto
serie = ana_.obter_vazoes(posto)

# obtenção da série histórica de cotas do posto fluviométrico 58235100
cotas = ana_.obter_cotas(posto)
```

### Cálculo da curva chave de um rio
![alt text](https://github.com/andradelis/hidro-os/blob/main/exemplos/curva_chave.png?raw=true)


### Estatísticas gerais de uma série
![alt text](https://github.com/andradelis/hidro-os/blob/main/exemplos/serie_mlt.png?raw=true)


### Hidrograma de cheias
![alt text](https://github.com/andradelis/hidro-os/blob/main/exemplos/hidrograma.png?raw=true)

