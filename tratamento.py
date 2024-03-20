import csv
import re

# Caminho do arquivo CSV de entrada
arquivo_entrada = '/Users/helbertwilliamduarteteixeira/Desktop/Desk/Logica/meu_ambiente/pyplan/LAYOUT STREAMLIT.csv'
# Caminho do arquivo CSV de saída
arquivo_saida = '/Users/helbertwilliamduarteteixeira/Desktop/Desk/Logica/meu_ambiente/pyplan/LAYOUT TRATADO.csv'

# Função para verificar se o campo é um número com vírgula
def eh_numero_com_virgula(campo):
    return re.match(r'^\d+,\d+$', campo)

# Função para substituir vírgula por ponto em números
def substituir_virgula_por_ponto_em_numeros(linha):
    return [campo.replace(',', '.') if eh_numero_com_virgula(campo) else campo for campo in linha]

with open(arquivo_entrada, 'r', encoding='utf-8') as entrada, open(arquivo_saida, 'w', newline='', encoding='utf-8') as saida:
    leitor = csv.reader(entrada, delimiter=';')
    escritor = csv.writer(saida, delimiter=',')
    
    for linha in leitor:
        # Substitui vírgula por ponto em campos que são números
        linha_atualizada = substituir_virgula_por_ponto_em_numeros(linha)
        # Escreve a linha atualizada no arquivo de saída
        escritor.writerow(linha_atualizada)