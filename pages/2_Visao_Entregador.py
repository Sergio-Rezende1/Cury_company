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

st.set_page_config( page_title='Visão Entregadores', page_icon='✅', layout='wide')

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

            
def df_med_entr(df1):
    """
    Esta função retorna: Um DataFrame com os tempos médios por Entregador
    """
    cols = ['Delivery_person_ID', 'Delivery_person_Ratings']
    avaliacao_media = df1.loc[:, cols].groupby('Delivery_person_ID').mean()
    avaliacao_media.columns = ['Avg_Rates']
    avaliacao_media = avaliacao_media.reset_index()

    return avaliacao_media


def df_med_tran (df1):
    """
    Esta função retorna: Um daataframe com os tempos médios por transito
    """
    cols = ['Road_traffic_density', 'Delivery_person_Ratings']
    avaliacao_media = df1.loc[:, cols].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']})
    avaliacao_media.columns = ['Avg_Rates', 'Std']
    avaliacao_media = avaliacao_media.reset_index()

    return avaliacao_media


def df_Cond_cli (df1):
    """
    Esta função retorna: Um daataframe com os tempos médios por clima
    """
    avaliacao_media = df1.loc[:, cols].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})
    avaliacao_media.columns = ['Avg_Rates', 'Std']
    avaliacao_media = avaliacao_media.reset_index()
    
    return avaliacao_media


def classificacao (df1, top_asc):
    """
    Esta função retorna: Um daataframe com os entregadores mais lentos por cidade 
    """
    cols = ['Delivery_person_ID', 'City', 'Time_taken(min)']
    df1_aux = (df1.loc[:, cols]
               .groupby(['City', 'Delivery_person_ID'])
               .mean()
               .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
               .reset_index())
    
    aux1 = df1_aux.loc[df1_aux['City'] == 'Metropolitian', :].head(10)
    aux2 = df1_aux.loc[df1_aux['City'] == 'Semi-Urban', :].head(10)
    aux3 = df1_aux.loc[df1_aux['City'] == 'Urban', :].head(10)
    aux4 = pd.concat ([aux1, aux2, aux3]).reset_index(drop=True)
    st.dataframe(aux4, column_config={'City': 'City', 'Delivery_person_ID': 'Delivery_ID', 'Time_taken(min)': 'Time_taken' },
                         hide_index=True, use_container_width=True)   

                
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

#++++++++++++++++++++++++++++++++++++++++++
# Layout no Streamlit
#++++++++++++++++++++++++++++++++++++++++++

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )
with tab1:
    with st.container():
        st.subheader( 'Métricas Gerais' )
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            st.write( 'Entregadores' )
            maior = df1.loc[: ,'Delivery_person_Age'].max()
            col1.metric( 'Maior idade:', maior)

        with col2:
            st.write( '_' )        
            menor = df1.loc[: ,'Delivery_person_Age'].min()
            col2.metric( 'Menor idade:', menor)
        
        with col3:
            st.write( 'Veículo' )
            melhor = df1.loc[: ,'Vehicle_condition'].max()
            col3.metric( 'Maior avaliação:', melhor)
            
        with col4:
            st.write( '_' )
            pior = df1.loc[: ,'Vehicle_condition'].min()
            col4.metric( 'Pior Avaliação:', pior)
            
        st.divider()
            
    with st.container():
        st.subheader( 'Tempos Médios' )        
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.write( 'Média por Entregador' )
            avaliacao_media = df_med_entr(df1) 
            st.dataframe(avaliacao_media, hide_index=True, use_container_width=True) 
             
        with col2:
            st.write( 'Média por Transito' )
            avaliacao_media = df_med_tran (df1)
            st.dataframe(avaliacao_media, hide_index=True, use_container_width=True)
            
            st.write( 'Média por Clima' )
            cols = ['Weatherconditions', 'Delivery_person_Ratings']
            avaliacao_media = df_Cond_cli (df1)
            st.dataframe(avaliacao_media, hide_index=True, use_container_width=True)
                             
        st.divider()
        
    with st.container():
        st.subheader( 'Desempenho por cidade' )
        col1, col2 = st.columns(2, gap='medium')
        with col1:
            st.write( 'Os mais rápidos' )
            classificacao (df1, top_asc=True)
            
          
        with col2:
            st.write( 'Os mais lentos' )
            classificacao (df1, top_asc=False)
            
            
