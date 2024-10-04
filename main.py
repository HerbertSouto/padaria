import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import locale
import io
import urllib.parse  # Para escapamento de URL

# Definir a localidade para formatação de moeda
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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
    {"Produto": item, "Preço (R$)": locale.currency(info["valor"], grouping=True)}
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
    data_inicio = periodo
    data_fim = periodo

# Verificar se a data final é anterior à data inicial
if data_fim < data_inicio:
    st.error("A data de fim deve ser posterior ou igual à data de início.")
else:
    dias_selecionados = (data_fim - data_inicio).days + 1

    # Botão para acionar o cálculo
    if st.button("Calcular orçamento"):
        valor_total_geral = 0

        # Criação de uma lista para armazenar os resultados
        resultados = []
        mensagem_orcamento = "Orçamento Padaria:\n"

        # Exibir os resultados de cada item
        for item in itens_selecionados:
            valor_unitario = itens[item]["valor"]
            quantidade = quantidades[item]
            valor_total_item = valor_unitario * quantidade * dias_selecionados
            valor_total_geral += valor_total_item

            # Adicionar à lista de resultados
            resultados.append({
                "Item": item,
                "Valor Unitário": locale.currency(valor_unitario, grouping=True),
                "Quantidade": quantidade,
                "Dias Selecionados": dias_selecionados,
                "Valor Total": locale.currency(valor_total_item, grouping=True),
            })

            # Adicionar à mensagem de WhatsApp
            mensagem_orcamento += f"{item} - {quantidade} unidades x {dias_selecionados} dias = {locale.currency(valor_total_item, grouping=True)}\n"

        # Exibir o valor total geral
        st.write(f"**Valor Total Geral:** {locale.currency(valor_total_geral, grouping=True)}")

        # Exibir o orçamento diretamente na tela
        st.subheader("Resumo do Orçamento")
        for item in resultados:
            st.write(f"{item['Item']} - {item['Quantidade']} unidades x {item['Dias Selecionados']} dias = {item['Valor Total']}")

        # Adicionar o valor total à mensagem de WhatsApp
        mensagem_orcamento += f"\n**Valor Total Geral: {locale.currency(valor_total_geral, grouping=True)}**"

        # Criar um DataFrame com os resultados
        df_resultados = pd.DataFrame(resultados)

        # Salvar os resultados em CSV
        csv = df_resultados.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar orçamento como CSV",
            data=csv,
            file_name='orçamento_padaria.csv',
            mime='text/csv',
        )

        # Salvar os resultados em Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_resultados.to_excel(writer, index=False)
        excel_buffer.seek(0)

        st.download_button(
            label="Baixar orçamento como Excel",
            data=excel_buffer,
            file_name='orçamento_padaria.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        # Botão para direcionar ao WhatsApp com o orçamento em texto
        numero_telefone = "5511973298868"  # Substitua pelo número desejado
        mensagem_whatsapp_escapada = urllib.parse.quote(mensagem_orcamento)  # Escapar a mensagem
        link_whatsapp = f"https://wa.me/{numero_telefone}?text={mensagem_whatsapp_escapada}"
        
        st.markdown(f"[Enviar orçamento via WhatsApp]({link_whatsapp})", unsafe_allow_html=True)
