import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Configurando layout do dashboard como a primeira instrução
st.set_page_config(layout="wide")

st.title('Dashboard de Gerenciamento de Produtos')

# Adicionar um componente para upload de arquivo
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=['csv'])

if uploaded_file is None:
    # Exibir empty state com SVG simples
    empty_state_placeholder = st.empty()
    empty_state_html = """
        <div style="display: flex; justify-content: center; align-items: center; height: 300px;">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="100" height="100">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            <p style="margin-left: 10px; font-size: 20px;">Por favor, faça o upload de um arquivo CSV</p>
        </div>
    """
    empty_state_placeholder.markdown(empty_state_html, unsafe_allow_html=True)
else:
    # Ler o arquivo CSV carregado
    dados = pd.read_csv(uploaded_file, encoding='utf-8')

    # Função para limpar e converter campos numéricos entre aspas
    def limpar_converter_campo_numerico(campo):
        if isinstance(campo, str):
            # Remove as aspas, pontos e vírgulas
            campo_limpo = campo.replace('"', '').replace('.', '').replace(',', '')
            # Tenta converter para int, se possível
            try:
                return int(campo_limpo)
            except ValueError:
                return campo  # Retorna o campo original se a conversão falhar
        else:
            return campo

    # Aplica a função de limpeza e conversão para cada coluna que pode conter números
    colunas_numericas = ['Quant', 'MDD']  # Substitua por suas colunas numéricas reais
    for coluna in colunas_numericas:
        dados[coluna] = dados[coluna].apply(limpar_converter_campo_numerico)

    # Converter 'Data Val' e 'Data Fab' para datetime explicitamente
    dados['Data Val'] = pd.to_datetime(dados['Data Val'], errors='coerce')
    dados['Data Fab'] = pd.to_datetime(dados['Data Fab'], errors='coerce')
    dados = dados.replace('\.', '', regex=True)

        # Verificar se 'dados' está definido antes de usar
    if 'dados' in locals():

        # Função para calcular os dias restantes até a data de validade
        def dias_para_vencer(row):
            hoje = datetime.now()
            if pd.notnull(row['Data Val']):
                return (row['Data Val'] - hoje).days
            else:
                return float('nan')  # Retorna NaN se 'Data Val' for NaT

        # Função para calcular a quantidade estimada a ser consumida
        def qtd_estimada_consumir(row):
            dias_restantes = dias_para_vencer(row)
            if pd.notnull(dias_restantes):
                return min(dias_restantes * row['MDD'], row['Quant'])
            else:
                return float('nan')  # Retorna NaN se 'dias_restantes' for NaN

        # Função para calcular a idade atual do produto em porcentagem
        def idade_atual_porcentagem(row):
            if pd.notnull(row['Data Val']) and pd.notnull(row['Data Fab']):
                total_vida = (row['Data Val'] - row['Data Fab']).days
                idade_atual = (datetime.now() - row['Data Fab']).days
                return (idade_atual / total_vida) * 100 if total_vida != 0 else 0
            else:
                return float('nan')  # Retorna NaN se 'Data Val' ou 'Data Fab' for NaT

        # Função para calcular a idade ao fim do consumo em porcentagem
        def idade_fim_consumo(row):
            dias_consumir = qtd_estimada_consumir(row)
            if pd.notnull(dias_consumir) and pd.notnull(row['Data Val']) and pd.notnull(row['Data Fab']):
                total_vida = (row['Data Val'] - row['Data Fab']).days
                return ((dias_consumir + (datetime.now() - row['Data Fab']).days) / total_vida) * 100 if total_vida != 0 else 0
            else:
                return float('nan')  # Retorna NaN se algum dos valores for NaN ou NaT

        # Função para classificar o risco de vencimento
        def classificar_risco(dias):
            if dias <= 30:
                return 'Alto Risco'
            elif dias <= 90:
                return 'Médio Risco'
            else:
                return 'Baixo Risco'

        # Função para destacar riscos com cores
        def highlight_risco(val):
            color = ''
            if val == 'Alto Risco':
                color = 'red'  # Texto em vermelho para alto risco
            elif val == 'Médio Risco':
                color = 'orange'  # Texto em laranja para médio risco
            elif val == 'Baixo Risco':
                color = 'green'  # Texto em verde para baixo risco
            return f'color: {color}'

        # Função para calcular o total a perder
        def total_a_perder(row):
            return max(0, row['Quant'] - qtd_estimada_consumir(row))


        # Carregar os dados do CSV
        #csv_file = '/Users/helbertwilliamduarteteixeira/Desktop/Desk/Logica/meu_ambiente/pyplan/filial_teste.csv'
        #dados = pd.read_csv(csv_file, parse_dates=['Data Fab', 'Data Val'], encoding='utf-8')

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

        # Juntando os dados filtrados
        produtos_ordenados_por_risco = pd.concat([
            dados[dados['Risco'] == 'Alto Risco'].sort_values('Dias para Vencer'),
            dados[dados['Risco'] == 'Médio Risco'].sort_values('Dias para Vencer'),
            dados[dados['Risco'] == 'Baixo Risco'].sort_values('Dias para Vencer')
        ])

        # Exibindo os dados combinados
        st.header('Produtos Ordenados por Risco')

       # Colunas que serão exibidas
        colunas_para_exibir = ['Nome', 'Risco', 'Data Val', 'Quant', 'MDD', 'Qtd Estimada a Consumir']

        # Filtrar o DataFrame para exibir apenas as colunas desejadas
        dados_filtrados = dados[colunas_para_exibir]

        # Aplicar a função de destaque aos riscos no DataFrame filtrado
        styled_df = dados_filtrados.style.applymap(lambda x: highlight_risco(x), subset=['Risco'])

        # Exibir a tabela estilizada no Streamlit
        st.dataframe(styled_df, use_container_width=True)
        
        # Contagem de produtos por categoria de risco
        contagem_risco = dados.groupby('Risco')['Quant'].sum().reset_index()

        # Criar uma nova coluna combinando 'Risco' e 'Quant'
        contagem_risco['RiscoQuantidade'] = contagem_risco.apply(lambda x: f"{x['Risco']} ({x['Quant']})", axis=1)

        st.markdown('##')

        # Colocando gráficos de histograma lado a lado
        col1, spacer, col2 = st.columns([1, 0.1, 1])

        with col1:
            # Histograma para idade atual (%)
            hist_age_current = alt.Chart(dados).mark_bar().encode(
                alt.X('Idade Atual (%):Q', bin=True), 
                y='count()',
                color=alt.Color('Idade Atual (%)', scale=alt.Scale(range=['#FF5733', '#33FF57']))  # Personalizando as cores
            ).properties(
                title='Distribuição da Idade Atual dos Produtos (%)'
            )
            st.altair_chart(hist_age_current, use_container_width=True)

        with col2:
            # Histograma para idade ao fim do consumo (%)
            hist_age_consumption = alt.Chart(dados).mark_bar().encode(
                alt.X('Idade ao Fim do Consumo (%):Q', bin=True),
                y='count()',
                color=alt.Color('Idade ao Fim do Consumo (%)', scale=alt.Scale(scheme='viridis'))  # Esquema de cores predefinido
            ).properties(
                title='Distribuição da Idade ao Fim do Consumo dos Produtos (%)'
            )
            st.altair_chart(hist_age_consumption, use_container_width=True)

        st.markdown('##')

        # Colocando gráficos de histograma lado a lado
        col4, spacer, col5 = st.columns([1, 0.1, 1])
    
        #Contagem de produtos por categoria de risco
        contagem_risco = dados.groupby('Risco').size().reset_index(name='Quant')

        # Calcular a porcentagem de cada categoria de risco
        total = contagem_risco['Quant'].sum()
        contagem_risco['Porcentagem'] = (contagem_risco['Quant'] / total * 100).round(1)
        
        with col4:
            st.markdown('##')
            st.markdown('##')
            st.markdown('##')
            # Gráfico de barras para risco de vencimento
            bar_chart_risk = alt.Chart(dados).mark_bar().encode(
                x=alt.X('count()', title='Quantidade'),
                y=alt.Y('Risco', sort='-x'),
                color=alt.Color('Risco', scale=alt.Scale(range=['#FF5733', '#33FF57']))  # Personalizando as cores
            ).properties(
                title='Contagem de Produtos por Categoria de Risco'
            )
            st.altair_chart(bar_chart_risk, use_container_width=True)
                    
        with col5:
            # Gráfico de barras para dias para vencer
            bar_chart_expiry = alt.Chart(dados).mark_bar().encode(
                x='Dias para Vencer',
                y='count()',
                color=alt.Color('Risco', scale=alt.Scale(scheme='category10'))  # Esquema de cores predefinido
            ).properties(
                title='Distribuição de Produtos por Dias para Vencer'
            )
            st.altair_chart(bar_chart_expiry, use_container_width=True)