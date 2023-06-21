import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="✅")

# image_path = 'C:/Users/Sergio/Dropbox\PC (2)/Documents/Repos/analisando_dados_com_python/ciclo6/Delivery1.png'
# O arquivo Delivery1.png, foi movidod para a mesma pasta do arquivo Home.py
image = Image.open( 'Delivery1.png' )
st.sidebar.image( image, width = 200 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as métricas de crescimento da Cury Company, Entregadores e Restaurantes.
    ### Como utilizaresse Dashboard.
    - Visão Empresa:
        - Visão Gerencial: Metricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    """)
    







































    

