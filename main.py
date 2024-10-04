import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import io
import urllib.parse  # Para escapamento de URL

# Função para formatar valores monetários manualmente
def formatar_moeda(valor):
    return f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Definir os itens disponíveis e seus valores unitários
itens = {
    "Pão Francês": {"valor": 1.5},
    "Pão Francês com Margarina": {"valor": 3.0},
    "Pão de Leite": {"valor": 2.0},
    "Pão de Leite com Margarina": {"valor": 3.5},
    "Pão Doce Recheado": {"valor": 3.0},
    "Rosquinha Canela e Açúcar": {"valor": 3.0},
    "Broa de Milho": {"valor": 4.0},
    "Pão Carteira": {"valor": 2.5},
    "Pão Carteira com Margarina": {"valor": 4.0},
    "Bolo de Milho": {"valor": 25.0},
    "Bolo de Caçarola": {"valor": 25.0},
    "Café (Litro)": {"valor": 15.0},
    "Leite (Litro)": {"valor": 15.0},
    "Chá (Litro)": {"valor": 12.0},
}

# Título do aplicativo
st.title("Calculadora de Orçamento - Padaria")

# Criar um DataFrame para exibir os preços em uma tabela interativa
tabela_itens = pd.DataFrame([
    {"Produto": item, "Preço (R$)": formatar_moeda(info["valor"])}
    for item, info in itens.items()
])

# Exibir a tabela de itens e preços
st.subheader("Lista de Produtos e Preços")
st.dataframe(tabela_itens, use_container_width=True)

# Selecionar os itens (multiselect)
itens_selecionados = st.multiselect("Escolha os itens", list(itens.keys()))

# Dicionário para armazenar a quantidade de cada item
quantidades = {}

# Inserir a quantidade para cada item selecionado
for item in itens_selecionados:
    quantidades[item] = st.number_input(f"Quantidade de {item}", min_value=1, value=1, key=item)

# Selecionar o intervalo de datas (frequência) em um único campo
periodo = st.date_input("Selecione o período", value=[datetime.today(), datetime.today() + timedelta(days=1)], 
                        min_value=datetime.today(), max_value=datetime.today() + timedelta(days=365), 
                        format="DD/MM/YYYY")

# Verificar se foi selecionado apenas um dia ou um intervalo de dias
if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    data_inicio, data_fim = periodo
else:
