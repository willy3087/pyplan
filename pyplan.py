import pandas as pd
from datetime import datetime

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

# Carregar os dados do CSV
csv_file = '/Users/helbertwilliamduarteteixeira/Desktop/Desk/Logica/pyplan/filial_teste.csv'  # Substitua pelo caminho correto do arquivo
dados = pd.read_csv(csv_file, parse_dates=['Data Fab', 'Data Val'], encoding='cp1252')

# Aplicar as funções para calcular os dias restantes, a quantidade estimada a consumir e classificar o risco
dados['Dias para Vencer'] = dados.apply(dias_para_vencer, axis=1)
dados['Qtd Estimada a Consumir'] = dados.apply(qtd_estimada_consumir, axis=1)
dados['Risco'] = dados['Dias para Vencer'].apply(classificar_risco)

# Identificar produtos a serem priorizados para consumo, ordenando-os pelo risco e pela idade
produtos_prioridade = dados.sort_values(by=['Risco', 'Data Fab'], ascending=[True, True])

# Identificar produtos prováveis de serem descartados (quantidade atual maior que a quantidade estimada a ser consumida)
produtos_descarte = dados[dados['Quant'] > dados['Qtd Estimada a Consumir']]

# Salvar os resultados
# Salvar os resultados
nomes_arquivos = ['produtos_prioridade.csv', 'produtos_descarte.csv']
produtos_prioridade.to_csv('produtos_prioridade.csv', index=False)
produtos_descarte.to_csv('produtos_descarte.csv', index=False)

for nome_arquivo in nomes_arquivos:
    print(f"{nome_arquivo} criado com sucesso!")

    # GRAFICO - visualizar a relação entre 'Dias para Vencer' e 'Qtd Estimada a Consumir'
bar_chart_risk = alt.Chart(dados).mark_bar().encode(
    x='count()',
    y=alt.Y('Risco', sort='-x'),
    color='Risco'
).properties(
    title='Contagem de Produtos por Categoria de Risco'
)

st.altair_chart(bar_chart_risk, use_container_width=True)

# GRAFICO - Gráfico de Barras Empilhadas para Produtos Próximos do Vencimento:
bar_chart_expiry = alt.Chart(dados).mark_bar().encode(
    x='Dias para Vencer',
    y='count()',
    color='Risco',
    tooltip=['Dias para Vencer', 'count()']
).properties(
    title='Distribuição de Produtos por Dias para Vencer'
)

st.altair_chart(bar_chart_expiry, use_container_width=True)

# GHRAFICO - Tabela de Produtos Prioritários para Ações:
produtos_alto_risco = dados[dados['Risco'] == 'Alto Risco'].sort_values('Dias para Vencer')
st.write("Produtos de Alto Risco (ordenados por Dias para Vencer):")
st.dataframe(produtos_alto_risco)

# GHRAFICO - Scatter Plot para Relação entre Dias para Vencer e Quantidade Estimada a Consumir:
scatter_plot = alt.Chart(dados).mark_circle(size=60).encode(
    x='Dias para Vencer',
    y='Qtd Estimada a Consumir',
    color='Risco',
    tooltip=['Nome', 'Dias para Vencer', 'Qtd Estimada a Consumir', 'Risco']
).properties(
    title='Relação entre Dias para Vencer e Quantidade Estimada a Consumir por Risco'
).interactive()

st.altair_chart(scatter_plot, use_container_width=True)

# GHRAFICO - Histogramas de Idade Atual (%) e Idade ao Fim do Consumo (%):
# Idade Atual (%)
hist_age_current = alt.Chart(dados).mark_bar().encode(
    alt.X('Idade Atual (%):Q', bin=True), 
    y='count()'
).properties(
    title='Distribuição da Idade Atual dos Produtos (%)'
)

st.altair_chart(hist_age_current, use_container_width=True)

# Idade ao Fim do Consumo (%)
hist_age_consumption = alt.Chart(dados).mark_bar().encode(
    alt.X('Idade ao Fim do Consumo (%):Q', bin=True),
    y='count()'
).properties(
    title='Distribuição da Idade ao Fim do Consumo dos Produtos (%)'
)

st.altair_chart(hist_age_consumption, use_container_width=True)