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
import numpy as np

st.set_page_config( page_title='Visão Restaurantes', page_icon='✅', layout='wide')

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
    
    # Criar a coluna 'Week_of_year'
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    # Criar a coluna 'Distancia' 
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['Distancia'] = df1.loc[: , cols].apply ( lambda x:
                          haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )


    # Reindexando o dataframe
    df1 = df1.reset_index(drop=True)
    
    return df1

def distancia (df1):
    """
    Calcula a distancia média entre os clientes e o restaurante
    """
    col = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1_aux = ( df1.loc[: , col].apply ( lambda x:haversine(
                                                            (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 ))
    distancia_media = np.round(df1_aux.mean(), 2 )

    return distancia_media


def graf_sunburst (df1):
    """
    Plota um grafico Sunburst com os seguintes itens: Cidade, tempo de entrega e transito
    """
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df1_aux = df1.loc[: , cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['Avg_time', 'Std']
    df1_aux = df1_aux.reset_index()
    fig = px.sunburst(df1_aux, path=['City', 'Road_traffic_density'], values='Avg_time',
                    color='Std', color_continuous_scale='Inferno',
                    color_continuous_midpoint=np.average(df1_aux['Std']))

    return fig


def graf_temp_med_std (df1):
    """
    Plota um grafico de barra com a média e desvio padrão do tempo de entrega por ciddade
    """
    cols = ['City', 'Time_taken(min)']
    df1_aux = df1.loc[: , cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['Avg_time', 'Std']
    df1_aux = df1_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',
                          x=df1_aux['City'],
                          y=df1_aux['Avg_time'],
                          error_y=dict( type='data', array=df1_aux['Std'])))
    fig.update_layout(barmode='group')

    return fig

def graf_dist_med (df1):
    """
    Plota um grafico de barras com a distância média entre restaurantes e clientes por cidade
    """
    distancia_media = df1.loc[:, ['City', 'Distancia']].groupby('City').mean().reset_index()
    #  Troquei o gráfico de pizza por de barras, pois faz mais sentido
    fig = px.bar(distancia_media, x='City', y='Distancia')

    return fig

def dat_med_std_cid_ped (df1):
    """
    exibe um DataFrame com o tempo médio e STD de entrega por cidade e tipo de pedido
    """
    cols = ['City', 'Time_taken(min)', 'Type_of_order']
    df1_aux = df1.loc[: , cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['Avg_time', 'Std']
    df1_aux = df1_aux.reset_index()

    return df1_aux

    
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
st.header('Marketplace - Visão Entregadores')

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
    'Condições de trânsito:',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""___""")

weatherconditions = st.sidebar.multiselect(
    'Condições do tempo:',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'] )


st.sidebar.markdown("""___""")

city = st.sidebar.multiselect(
    'Cidades:',
    ['Metropolitian', 'Semi-Urban', 'Urban' ],
    default=['Metropolitian', 'Semi-Urban', 'Urban'] )

st.sidebar.markdown("""___""")

order = st.sidebar.multiselect(
    'Pedido:',
    ['Buffet', 'Drinks', 'Meal', 'Snack' ],
    default=['Buffet', 'Drinks', 'Meal', 'Snack' ] )

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

# Filtro de condições Climáticas
linhas_selecionadas = df1['Weatherconditions'].isin( weatherconditions )
df1 = df1.loc[ linhas_selecionadas, :]

# Filtro de cidades
linhas_selecionadas = df1['City'].isin( city )
df1 = df1.loc[ linhas_selecionadas, :]

# Filtro de tipo de pedido
linhas_selecionadas = df1['Type_of_order'].isin( order )
df1 = df1.loc[ linhas_selecionadas, :]

#++++++++++++++++++++++++++++++++++++++++++
# Layout no Streamlit
#++++++++++++++++++++++++++++++++++++++++++

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )
with tab1:
    with st.container():
        st.subheader( 'Métricas Gerais' )
        col1, col2 = st.columns(2, gap='small')
        
        with col1:
            st.write( 'Entregadores únicos' )
            unicos = df1['Delivery_person_ID'].nunique()
            col1.metric( '', unicos)

        with col2:
            st.write( 'Distância média' )          
            distancia_media = distancia (df1)
            col2.metric( '', distancia_media)

        col1, col2, col3, col4 = st.columns(4, gap='small')
        with col1:
            st.write( 'Tempo de entrega' )
            df1_aux = df1.loc[: , ['Festival', 'Time_taken(min)']].groupby('Festival').mean().reset_index()
            col1.metric( 'Média c/ Festival', np.round(df1_aux.iloc[1, 1],2))
            
        with col2:
            st.write( '_' )
            df1_aux = df1.loc[: , ['Festival', 'Time_taken(min)']].groupby('Festival').std().reset_index()            
            col2.metric( 'STD c/ Festival', np.round(df1_aux.iloc[1, 1],2))

        with col3:           
            st.write( '_' )
            df1_aux = df1.loc[: , ['Festival', 'Time_taken(min)']].groupby('Festival').mean().reset_index()            
            col3.metric( 'Média s/ Festival', np.round(df1_aux.iloc[0, 1],2))
            
        with col4:
            st.write( '_' ) 
            df1_aux = df1.loc[: , ['Festival', 'Time_taken(min)']].groupby('Festival').std().reset_index()               
            col4.metric( 'STD s/ Festival', np.round(df1_aux.iloc[0, 1],2))        
           
        st.divider()
           
    with st.container():
        st.subheader('Média e STD de entrega por cidade e tipo de tráfego.')
        fig = graf_sunburst (df1)
        st.plotly_chart(fig, use_container_width=True) 

        st.divider()
        
    with st.container():
        st.subheader( 'Distribuição do tempo' )        

        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.write('Média e STD de entrega por cidade')
            fig = graf_temp_med_std (df1)
            st.plotly_chart(fig, use_container_width=True)             
            
        with col2:
            st.write( 'Distância média das entregas por cidade' )
            fig = graf_dist_med (df1)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        
    with st.container():
        st.subheader( 'Tempo médio e STD de entrega por cidade e tipo de pedido' )
        df1_aux = dat_med_std_cid_ped (df1)
        st.dataframe(df1_aux, hide_index=True, use_container_width=True)

