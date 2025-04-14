pip install yfinance
# Importar as bibliotecas
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
 
# Criar as funções de carregamento de dados
    # Cotações de ações - 2020 a 2024
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = ' '.join(empresas) # Juntar os tickers em uma string separados por espaço
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period='1d', start='2020-01-01', end='2024-07-01')
    cotacoes_acao = cotacoes_acao['Close']
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv('IBOV.csv', sep=';', index_col=False)
    tickers = list(base_tickers['Codigo'])
    tickers = [item + ".SA" for item in tickers]
    return tickers

acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)

# Criar a interface do Streamlit
st.write("""
        # App Preço de Ações
        O gráfico abaixo representa a evolução do preço das ações ao longo dos anos de 2010 e 2024.
        """) # Markdown

# Preparar as visualizações (filtros)
st.sidebar.header('Filtros')

# Filtro de ações
lista_acoes = st.sidebar.multiselect('Escolha as ações para visualizar', dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: 'Close'})

# Filtros de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider('Selecione o período',
                                   min_value=data_inicial,
                                   max_value=data_final,
                                   value=(data_inicial, data_final),
                                   step=timedelta(days=1)
                                   )
dados = dados.loc[intervalo_data[0]:intervalo_data[1]] # Filtrar os dados com base no intervalo de datas selecionado

# Criar o gráfico
st.line_chart(dados)

# Calcular a performance dos ativos
texto_performance_ativos = ''
if len(lista_acoes) == 0:
    lista_acoes = dados.columns # Se nenhuma ação for selecionada, usar todas as ações disponíveis
elif len(lista_acoes) == 1:
    dados = dados.rename(columns={'Close': acao_unica}) # Renomear a coluna para 'Close' se apenas uma ação for selecionada

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    # :cor[texto]
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1 # Calcular a performance do ativo
    performance_ativo = float(performance_ativo)

    carteira[i] = carteira[i] * (1 + performance_ativo) # Atualizar o valor da carteira com a performance do ativo

    if performance_ativo > 0:
        texto_performance_ativos = texto_performance_ativos + f'  \n {acao}: :green[{performance_ativo:.1%}]' # Formatar a performance do ativo como porcentagem
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f'  \n {acao}: :red[{performance_ativo:.1%}]'
    else:
        texto_performance_ativos = texto_performance_ativos + f'  \n {acao}: {performance_ativo:.1%}'

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1 # Calcular a performance da carteira

if performance_carteira > 0:
    texto_performance_carteira = f"Performance da certeira com todos os ativos: :green[{performance_carteira:.1%}]"
elif performance_carteira < 0:
    texto_performance_carteira = f"Performance da certeira com todos os ativos: :red[{performance_carteira:.1%}]"
else:
    texto_performance_carteira = f"Performance da certeira com todos os ativos: {performance_carteira:.1%}"

st.write(f"""
### Performance dos Ativos
Essa foi a performance de cada ativo no período selecionado:
{texto_performance_ativos}

{texto_performance_carteira}
""")
