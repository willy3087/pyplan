import csv
import re

# Caminho do arquivo CSV de entrada
arquivo_entrada = '/Users/helbertwilliamduarteteixeira/Desktop/Desk/Logica/meu_ambiente/pyplan/LAYOUT STREAMLIT.csv'
# Caminho do arquivo CSV de saída
arquivo_saida = '/Users/helbertwilliamduarteteixeira/Desktop/Desk/Logica/meu_ambiente/pyplan/LAYOUT TRATADO.csv'

# Função para remover todas as vírgulas de campos que contêm dígitos
def remover_virgulas_em_numeros(campo):
    # Verifica se o campo contém dígitos e possivelmente vírgulas
    if re.match(r'^[\d,]+$', campo):
        return campo.replace(',', '').replace('.', '') # Remove todas as vírgulas e pontos
    else:
        return campo

# Função para substituir "/" por "-" em datas
def substituir_barra_por_hifen_em_datas(campo):
    return campo.replace('/', '-') if '/' in campo else campo

# Função para remover campos vazios de uma linha
def remover_campos_vazios(linha):
    return [campo for campo in linha if campo.strip() != '']

def limpar_e_converter_numero(campo):
    # Remove aspas, pontos e vírgulas
    campo_limpo = re.sub(r'[",.]', '', campo)
    # Tenta converter para inteiro
    try:
        return int(campo_limpo)
    except ValueError:
        # Se falhar, tenta converter para float
        try:
            return float(campo_limpo)
        except ValueError:
            # Se ainda falhar, retorna o campo original
            return campo

with open(arquivo_entrada, 'r', encoding='utf-8') as entrada, open(arquivo_saida, 'w', newline='', encoding='utf-8') as saida:
    leitor = csv.reader(entrada, delimiter=';')
    escritor = csv.writer(saida, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    
    for linha in leitor:
        # Aplica a função de limpeza e conversão para cada campo da linha
        linha_atualizada = [limpar_e_converter_numero(campo) for campo in linha]
        # Escreve a linha atualizada no arquivo de saída
        # Remove todas as vírgulas em campos que contêm dígitos
        linha_atualizada = [remover_virgulas_em_numeros(campo) for campo in linha]
        # Substitui "/" por "-" em campos de data
        linha_atualizada = [substituir_barra_por_hifen_em_datas(campo) for campo in linha_atualizada]
        # Remove campos vazios da linha atualizada
        linha_sem_campos_vazios = remover_campos_vazios(linha_atualizada)
        # Escreve a linha sem campos vazios no arquivo de saída
        escritor.writerow(linha_sem_campos_vazios)