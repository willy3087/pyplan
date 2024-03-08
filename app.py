import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from vega_datasets import data

# Função para calcular os dias restantes até a data de validade
def dias_para_vencer(row):
    hoje = datetime.now()
    return (row['Data Val'] - hoje).days

# Função para calcular a quantidade estimada a ser consumida
def qtd_estimada_consumir(row):
    dias_restantes = dias_para_vencer(row)
    return min(dias_restantes * row['MDD'], row['Quant'])

# Função para classificar o risco de vencimento
def classificar_risco(dias):
    if dias <= 30:
        return 'Alto Risco'
    elif dias <= 90:
        return 'Médio Risco'
    else:
        return 'Baixo Risco'

# Função para calcular a idade atual do produto em porcentagem
def idade_atual_porcentagem(row):
    total_vida = (row['Data Val'] - row['Data Fab']).days
    idade_atual = (datetime.now() - row['Data Fab']).days
    return (idade_atual / total_vida) * 100 if total_vida != 0 else 0

# Função para calcular a idade ao fim do consumo em porcentagem
def idade_fim_consumo(row):
    dias_consumir = min(row['Dias para Vencer'], qtd_estimada_consumir(row) / row['MDD'])
    total_vida = (row['Data Val'] - row['Data Fab']).days
    return ((dias_consumir + (datetime.now() - row['Data Fab']).days) / total_vida) * 100 if total_vida != 0 else 0

# Função para calcular o total a perder
def total_a_perder(row):
    return max(0, row['Quant'] - qtd_estimada_consumir(row))

# Carregar os dados do CSV
csv_file = '/Users/helbertwilliamduarteteixeira/Desktop/Desk/Logica/meu_ambiente/pyplan/filial_teste.csv'
dados = pd.read_csv(csv_file, parse_dates=['Data Fab', 'Data Val'], encoding='cp1252')

# Aplicar as funções para calcular os dias restantes, a quantidade estimada a ser consumir, classificar o risco
dados['Dias para Vencer'] = dados.apply(dias_para_vencer, axis=1)
dados['Qtd Estimada a Consumir'] = dados.apply(qtd_estimada_consumir, axis=1)
dados['Risco'] = dados['Dias para Vencer'].apply(classificar_risco)
dados['Idade Atual (%)'] = dados.apply(idade_atual_porcentagem, axis=1)
dados['Idade ao Fim do Consumo (%)'] = dados.apply(idade_fim_consumo, axis=1)
dados['Total a Perder'] = dados.apply(total_a_perder, axis=1)

# Identificar produtos a serem priorizados para consumo, ordenando-os pelo risco e pela idade atual em porcentagem
produtos_prioridade = dados.sort_values(by=['Risco', 'Idade Atual (%)'], ascending=[True, False])

# Identificar produtos prováveis de serem descartados (quantidade atual maior que a quantidade estimada a ser consumida)
produtos_descarte = dados[dados['Quant'] > dados['Qtd Estimada a Consumir']]

# Salvar os resultados
nomes_arquivos = ['produtos_prioridade.csv', 'produtos_descarte.csv']
produtos_prioridade.to_csv('produtos_prioridade.csv', index=False)
produtos_descarte.to_csv('produtos_descarte.csv', index=False)

# Configurando layout do dashboard
st.set_page_config(layout="wide")

st.title('Dashboard de Gerenciamento de Produtos')

# Tabela de produtos de alto risco com filtragem
st.header('Produtos de Alto Risco (ordenados por Dias para Vencer)')
produtos_alto_risco = dados[dados['Risco'] == 'Alto Risco'].sort_values('Dias para Vencer')
produtos_medio_risco = dados[dados['Risco'] == 'Médio Risco'].sort_values('Dias para Vencer')
produtos_baixo_risco = dados[dados['Risco'] == 'Baixo Risco'].sort_values('Dias para Vencer')
st.dataframe(produtos_alto_risco.style.highlight_max(axis=0, color='red'), use_container_width=True)  # Tabela flexível
st.dataframe(produtos_medio_risco.style.highlight_max(axis=0, color='yellow'), use_container_width=True)  # Tabela flexível
st.dataframe(produtos_baixo_risco.style.highlight_max(axis=0, color='green'), use_container_width=True)  # Tabela flexível

# Layout de duas colunas para os gráficos de barra
col1, col2 = st.columns(2)

with col1:
    # Histograma para idade atual (%)
    hist_age_current = alt.Chart(dados).mark_bar().encode(
        alt.X('Idade Atual (%):Q', bin=True), 
        y='count()',
        color=alt.value("steelblue")  # Cor fixa, mas você pode personalizar
    ).properties(
        title='Distribuição da Idade Atual dos Produtos (%)'
    )
    st.altair_chart(hist_age_current, use_container_width=True)

with col2:
    # Histograma para idade ao fim do consumo (%)
    hist_age_consumption = alt.Chart(dados).mark_bar().encode(
        alt.X('Idade ao Fim do Consumo (%):Q', bin=True),
        y='count()',
        color=alt.value("salmon")  # Cor fixa, mas você pode personalizar
    ).properties(
        title='Distribuição da Idade ao Fim do Consumo dos Produtos (%)'
    )
    st.altair_chart(hist_age_consumption, use_container_width=True)

# Colocando gráficos de histograma lado a lado
col3, col4 = st.columns(2)

with col3:
    # Gráfico de barras para risco de vencimento
    bar_chart_risk = alt.Chart(dados).mark_bar().encode(
        x=alt.X('count()', title='Quantidade'),
        y=alt.Y('Risco', sort='-x'),
        color='Risco'
    ).properties(
        title='Contagem de Produtos por Categoria de Risco'
    )
    st.altair_chart(bar_chart_risk, use_container_width=True)
    st.write(dados['Risco'].unique())

with col4:
    # Gráfico de barras para dias para vencer
    bar_chart_expiry = alt.Chart(dados).mark_bar().encode(
        x='Dias para Vencer',
        y='count()',
        color='Risco',
        tooltip=['Dias para Vencer', 'count()']
    ).properties(
        title='Distribuição de Produtos por Dias para Vencer'
    )
    st.altair_chart(bar_chart_expiry, use_container_width=True)


# GHRAFICO -


# Exibir os resultados no dashboard
#'''st.write("Produtos Priorizados para Consumo (ordenados por risco e idade atual):")
#st.dataframe(produtos_prioridade)

#st.write("Produtos Prováveis de Serem Descartados:")
#st.dataframe(produtos_descarte'''