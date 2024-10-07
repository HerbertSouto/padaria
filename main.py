import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import io
import urllib.parse  # Para escapamento de URL
import numpy as np

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
st.title("Orçamento de encomendas - Padaria Guilherme e Gabriel")

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

# Selecionar o intervalo de datas usando um seletor de datas (calendário)
periodo = st.date_input("Selecione o período (um ou mais dias)", 
                        value=[datetime.today(), datetime.today() + timedelta(days=1)], 
                        min_value=datetime.today(), 
                        max_value=datetime.today() + timedelta(days=365), 
                        format="DD/MM/YYYY")

# Verificar se foi selecionado apenas um dia ou um intervalo de dias
if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    data_inicio, data_fim = periodo
else:
    data_inicio = periodo
    data_fim = periodo

# Permitir que o usuário exclua os finais de semana
excluir_finais_semana = st.checkbox("Excluir finais de semana")

# Lista para armazenar as datas selecionadas
datas_selecionadas = pd.date_range(start=data_inicio, end=data_fim)

# Filtrar finais de semana se a opção for marcada
if excluir_finais_semana:
    datas_selecionadas = datas_selecionadas[~datas_selecionadas.weekday.isin([5, 6])]

# Oferecer ao usuário a opção de excluir dias específicos manualmente
dias_para_excluir = st.multiselect("Selecione dias a excluir (opcional)", datas_selecionadas)

# Filtrar os dias que foram selecionados para excluir
datas_selecionadas = [data for data in datas_selecionadas if data not in dias_para_excluir]

# Verificar se o período filtrado contém ao menos um dia
if len(datas_selecionadas) == 0:
    st.error("Nenhum dia válido foi selecionado. Por favor, ajuste o período ou as exclusões.")
else:
    dias_selecionados = len(datas_selecionadas)

    # Botão para acionar o cálculo
    if st.button("Calcular orçamento"):
        valor_total_geral = 0

        # Criação de uma lista para armazenar os resultados
        resultados = []
        mensagem_orcamento = "Olá, gostaria de falar sobre meu orçamento:\n"

        # Exibir os resultados de cada item
        for item in itens_selecionados:
            valor_unitario = itens[item]["valor"]
            quantidade = quantidades[item]
            valor_total_item = valor_unitario * quantidade * dias_selecionados
            valor_total_geral += valor_total_item

            # Adicionar à lista de resultados
            resultados.append({
                "Item": item,
                "Valor Unitário": formatar_moeda(valor_unitario),
                "Quantidade": quantidade,
                "Dias Selecionados": dias_selecionados,
                "Valor Total": formatar_moeda(valor_total_item),
            })

            # Adicionar à mensagem de WhatsApp
            mensagem_orcamento += f"{item} - {quantidade} unidades x {dias_selecionados} dias = {formatar_moeda(valor_total_item)}\n"

        # Exibir o valor total geral
        st.write(f"**Valor Total:** {formatar_moeda(valor_total_geral)}")

        # Exibir o orçamento diretamente na tela, com visualização mais bonita
        st.subheader("Resumo")
        st.markdown("<style>th {background-color: #f0f0f0;}</style>", unsafe_allow_html=True)
        st.table(pd.DataFrame(resultados))  # Remove o índice

        # Adicionar o valor total à mensagem de WhatsApp
        mensagem_orcamento += f"\n**Valor Total: {formatar_moeda(valor_total_geral)}**"

        # Criar um DataFrame com os resultados
        df_resultados = pd.DataFrame(resultados)

        # Salvar os resultados em CSV
        csv = df_resultados.to_csv(index=False).encode('utf-8')
        
        # Colocar os botões de download lado a lado
        col1, col2 = st.columns(2)

        with col1:
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
        with col2:
            st.download_button(
                label="Baixar orçamento como Excel",
                data=excel_buffer,
                file_name='orçamento_padaria.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )

        # Criar um link para envio do orçamento via WhatsApp
        mensagem_wa = urllib.parse.quote(mensagem_orcamento)
        whatsapp_link = f"https://wa.me/5511973298868?text={mensagem_wa}"

        # Adicionar o botão para enviar orçamento via WhatsApp centralizado e mais abaixo
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 30px;">
                <a href="{whatsapp_link}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #25D366;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        font-size: 16px;
                        cursor: pointer;
                    ">Fale conosco via WhatsApp</button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
