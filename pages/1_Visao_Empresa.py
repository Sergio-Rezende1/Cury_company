# importando libraries
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine

# Bibliotecas necessárias
import pandas as pd
import streamlit as st
import datetime as dt
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='✅', layout='wide')

#++++++++++++++++++++++++++++++++++++++++++
# Funções
#++++++++++++++++++++++++++++++++++++++++++


def clean_code(df1):
    """ 
    Esta função tem a responsabilidade de limpar e preparar o Dataframe para as analises

    1 . Remoção das linhas com 'NaN'
    2 . Correção dos tipo de dados
    3 . Ajustando conteudo dos campos da coluna 'Time_taken(min)'
    4 . Tirando espaços ' ' dos campos de texto
    5 . Criando novas colunas
    6 . Reindexando o Dataframe

    imput: Dataframe
    output: Dataframe
    """
    
    # Coluna 'Delivery_person_Age'
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # Coluna 'Delivery_person_Ratings'
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # Coluna 'Order_Date'
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format="%d-%m-%Y")
    
    # Coluna 'Multiple_deliveries'
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # Coluna 'City'
    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # Coluna 'Road_traffic_density'
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # Coluna 'Festival'
    linhas_selecionadas = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # Coluna 'Time Taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ') [1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    #Tirando os espaços de dentro dos campos do DataSet
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    
    # Criar a coluna da 'Week_of_year'
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    # Reindexando o dataframe
    df1 = df1.reset_index(drop=True)
    
    return df1

        
def quant_ped_dia (df1):
    """
    Este grafico plota:  Quantidade de pedidos por dia
    """
    colunas = ['ID', 'Order_Date']
    df1_aux = df1.loc[:, colunas].groupby('Order_Date').count().reset_index()
    fig = px.bar(df1_aux, x='Order_Date', y='ID')
    
    return fig


def dist_ded_traf (df1):
    """
    Este grafico plota: Distribuição de pedidos por tipo de tráfego
    """
    df1_aux = df1.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df1_aux = df1_aux.loc[df1_aux['Road_traffic_density'] != "NaN", :]
    df1_aux['IDs_perc'] = df1_aux['ID'] / df1_aux['ID'].sum()
    fig = px.pie(df1_aux, values='IDs_perc',names='Road_traffic_density')
    
    return fig


def vol_ped_cid (df1):
    """
    Este grafico plota: Comparação do volume de pedidos por cidade e tráfego
    """
    colunas = ['ID', 'City', 'Road_traffic_density']
    df1_aux = df1.loc[:, colunas].groupby(['City', 'Road_traffic_density']).nunique().reset_index()
    df1_aux = df1_aux.loc[(df1_aux['City'] != "NaN") & (df1_aux['Road_traffic_density'] != "NaN") , :]
    fig = px.scatter(df1_aux, x='City', y="Road_traffic_density", size="ID", color="City")            

    return fig


def quant_pep_sem (df1):
    """
    Este grafico plota: Quantidade de pédidos por semana
    """
    df1_aux = df1.loc[:,['Week_of_year', 'ID']].groupby('Week_of_year').count().reset_index()
    fig = px.line(df1_aux, x='Week_of_year', y="ID")

    return fig


def quant_ent_sem (df1):
    """
    Este gráfico plota: A quantidade de pedidos por entregador por semana
    """
    df1_aux = df1.loc[:, ['Week_of_year', 'Delivery_person_ID']].groupby('Week_of_year').nunique().reset_index()
    df2_aux = df1.loc[:, ['ID', 'Week_of_year']].groupby('Week_of_year').count().reset_index()
    df_aux = pd.merge(df1_aux, df2_aux, how= 'inner')
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_of_year', y='Order_by_delivery')

    return fig


def loc_cen_Cid (df1):
    """
    Este gráfico plota: A localização central de cada cidade por tipo de tráfego
    """
    df1_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ]]
                  .groupby(['City', 'Road_traffic_density']).median().reset_index())
    df1_aux = df1_aux.loc[(df1_aux['City'] != "NaN") & (df1_aux['Road_traffic_density'] != "NaN") , :]
    map = folium.Map(location=[19.894685, 79.191159], zoom_start=4, tiles="OpenStreetMap")

    for index, location_info in df1_aux.iterrows():
          folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], 
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)        
    folium_static( map, width=700, height=350 )

    
#++++++++++++++++++++++++++++++++++++++++++
# Estrutura  Logica do Código
#++++++++++++++++++++++++++++++++++++++++++
    
# Carregando dados
df = pd.read_csv('dataset/train.csv')

# Limpando Dataset
df1 = clean_code(df)

    
#++++++++++++++++++++++++++++++++++++++++++
# Layout Barra Lateral
#++++++++++++++++++++++++++++++++++++++++++
st.header('Marketplace - Visão Empresa')


image = Image.open( 'Delivery1.png' )
st.sidebar.image( image, width = 200 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual data?',
    value = dt.datetime( 2022, 4, 6 ),
    min_value=dt.datetime( 2022, 2, 11 ),
    max_value=dt.datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Comunidade DS")

#++++++++++++++++++++++++++++++++++++++++++
# Aplicando filtros ao DataFrame
#++++++++++++++++++++++++++++++++++++++++++

# Filtro de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[ linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, :]

#++++++++++++++++++++++++++++++++++++++++++
# Layout no Streamlit
#++++++++++++++++++++++++++++++++++++++++++

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        st.write("Quantidade de pedidos por dia")
        fig = quant_ped_dia (df1)
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

    with st.container():
        col1, col2 = st.columns( 2)
        with col1:
            st.write("Distribuição de pedidos por tipo de tráfego")
            fig = dist_ded_traf (df1)
            st.plotly_chart(fig, use_container_width=True)            
            
        with col2:
            st.write("Comparação do volume de pedidos por cidade e tráfego")
            fig = vol_ped_cid (df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.write("Quantidade de pédidos por semana")
        fig = quant_pep_sem (df1)
        st.plotly_chart(fig, use_container_width=True, width=600, height=200)                
        st.divider()
    
    with st.container():
        st.write("A quantidade de pedidos por entregador por semana")
        fig = quant_ent_sem (df1)
        st.plotly_chart(fig, use_container_width=True, height=350)        
            
with tab3:
    with st.container():
        st.write("A localização central de cada cidade por tipo de tráfego")
        loc_cen_Cid (df1)

