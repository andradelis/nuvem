# :construction: hidro-os
Repositório destinado a compartilhar meus aprendizados na área de hidrologia.

## Uso

O repositório está em construção! Mas, caso deseje, é possível utilizar algumas funcionalidades. :)

Para utilizar os métodos existentes, clone este repositório

`git clone git@github.com:andradelis/dados-hidro.git`

e instale as dependências necessárias

`pip install -r requirements.txt`

## Exemplos


Por enquanto, é possível obter a série de vazões e a série de cotas de um posto específico a partir dos dados da Agência Nacional das Águas, e calcular a curva chave de um rio. Mais novidades em breve.

### Acesso aos dados disponibilizados na API da Agência Nacional das Águas.

```
# importação da biblioteca
from src.ANA import ANA

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

#### Tratamento das saídas das séries da ANA

```
# fixando as medições de cota a um horário fixo de 7 horas da manhã
cotas = cotas[cotas.index.hour == 7]
cotas = cotas.resample("D").mean()

cotas_vazoes = cotas.merge(serie.vazoes, right_index = True, left_index = True)
cotas_vazoes.dropna(axis = 0, how = 'any', inplace = True)

dados_cchave = cotas_vazoes.set_index('cota')
dados_cchave.sort_index(inplace = True)

cotas = dados_cchave.index
vazoes = dados_cchave.vazoes
```

#### Curva chave

```
curva, coefs = curva_chave(cotas, vazoes) 

fig, ax = plt.subplots(figsize=(18, 6))

label='y = {:.4f}x² + {:.2f}x + ({:.2f})'.format(coefs[0], coefs[1], coefs[2])

ax.scatter(cotas, vazoes)
ax.plot(cotas, curva, color = 'red', lw=1, label = label)

ax.set_ylabel("Vazão (m³/s)")
ax.set_xlabel("Cota (m)")
ax.legend()
```

![alt text](https://github.com/andradelis/hidro-os/blob/main/exemplos/curva_chave.png?raw=true)



