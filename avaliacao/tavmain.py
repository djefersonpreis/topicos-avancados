import pandas as pd
import streamlit as st
import altair as alt
import plotly
import plotly.graph_objs as go 
from plotly import tools
from plotly.offline import init_notebook_mode, plot, iplot
import plotly.express as px 
from streamlit_folium import folium_static 
import folium
from folium.plugins import MarkerCluster

st.title('Trabalho II - Tópicos Avançados')


@st.cache
def load_database():
    return pd.read_feather('database/base.feather'), \
        pd.read_feather('database/classificacaoz_Customer ID.feather'), \
        pd.read_feather('database/classificacaoz_Category.feather'), \
        pd.read_feather('database/classificacaoz_Region.feather'), \
        pd.read_feather('database/classificacaoz_Segment.feather'), \
        pd.read_feather('database/clusterizacao_estado.feather'), \
        pd.read_feather('database/regressao_regiao.feather'), \
        pd.read_feather('database/regressao_segment.feather'), \
        pd.read_feather('database/localizacao.feather'), \
        pd.read_feather('database/estadosUS.feather')


base, cla_cus, cla_cat, cla_reg, cla_seg, clu_est, reg_reg, reg_seg, coords, estados = load_database()

rg_reg = reg_reg.copy()
rg_reg['ano'] = rg_reg['ds'].dt.year

rg_seg = reg_seg.copy()
rg_seg['ano'] = rg_seg['ds'].dt.year

coords = coords[coords['pais'] == 'United States']

# st.dataframe(base)
# st.dataframe(cla_cat)

taberp, tabbi, tabstone = st.tabs(['Sistema Interno', 'Gestão', 'E-Commerce'])

with taberp:
    st.header('Dados do Sistema Interno')

    # if st.checkbox('Consumidor'):
    consumidor = st.selectbox('Selecione o Consumidor',
                              base['Customer ID'].unique())
    base_con = base[base['Customer ID'] == consumidor].reset_index()
    # st.dataframe(base_con)
    cla_cus_con = cla_cus[cla_cus['Customer ID'] == consumidor].reset_index()
    # st.dataframe(cla_cus_con)

    st.dataframe(base_con[['Customer Name', 'Segment']].drop_duplicates())
    cl1, cl2, cl3, cl4 = st.columns(4)
    cl1.metric('Score', round(cla_cus_con['score'][0], 4), "1")
    cl2.metric('Classe', int(cla_cus_con['classe'][0]), "1")
    cl3.metric('Rank', int(cla_cus_con['rank'][0]), "1")
    cl4.metric('Lucro', int(cla_cus_con['lucro'][0]), "1")

    cl1.metric('Valor Total Comprado', round(base_con['Sales'].sum(), 2), '1')
    cl2.metric('Valor Lucro', round(base_con['Profit'].sum(), 2), '1')
    cl3.metric('Valor Médio Comprado', round(base_con['Sales'].mean(), 2), '1')
    cl4.metric('Quantidade Comprada', round(
        base_con['Quantity'].sum(), 2), '1')
    with st.expander('Pedidos:'):
        st.dataframe(
            base_con[['Order Date', 'Product Name', 'Quantity', 'Sales', 'Profit']])

    with st.expander('Cluster Estado:'):
        clu_est_cus = clu_est[clu_est['reference']
                              == base_con['State'].values[0]]
        st.dataframe(clu_est_cus[['cluster', 'm_sales', 'm_profit',
                     'm_quantity', 'r_days', 'f_sales', 'f_profit']])
        st.dataframe(clu_est_cus[['cluster', 'clm_sales', 'clm_profit',
                     'clm_quantity', 'clr_days', 'clf_sales', 'clf_profit']])

    with st.expander('Entregas (Mapa):'):
        coords_con = base_con[['Order ID', 'Order Date',
                               'Ship Date', 'Region', 'State', 'City', 'Profit']].copy()
        coords_con = coords_con.merge(
            coords, left_on=['City'], right_on=['cidade'], how='left')
        coords_con = coords_con.rename(columns={
            'lng': 'lon'
        })
        st.dataframe(
            coords_con[['Order ID', 'Order Date', 'Ship Date', 'Region', 'State', 'City']])
        st.map(coords_con)

        m = folium.Map(location=[0, 0], tiles='openstreetmap', zoom_start=2)
        for id,row in coords_con.iterrows():
            folium.Marker(location=[row['lat'],row['lon']], popup=row['Profit']).add_to(m)
        folium_static(m)

    with st.expander('Cluster de Pedidos (Mapa):'): 
        data_pedidos = base.copy()
        data_pedidos = data_pedidos.merge(coords, left_on=['City'], right_on=['cidade'], how='left')
        data_pedidos = data_pedidos.fillna(0) 

        m2 = folium.Map(location=[0,0], tiles='cartodbpositron', zoom_start=2)
        mc = MarkerCluster()
        for idx, row in data_pedidos.iterrows():
            mc.add_child(folium.Marker([row['lat'], row['lng']],popup=row['State']))
        m2.add_child(mc)
        folium_static(m2) 

    # if st.checkbox('Categoria'):

    #     categoria = st.selectbox('Selecione a Categoria', base['Category'].unique())
    #     base_cat = base[base['Category'] == categoria].reset_index()
    #     # st.dataframe(base_con)
    #     cla_cat_cat = cla_cat[cla_cat['Category'] == categoria].reset_index()
    #     # st.dataframe(cla_cat_cat)

    #     st.dataframe(base_cat[['Category']].drop_duplicates())
    #     cl1, cl2, cl3, cl4 = st.columns(4)
    #     cl1.metric('Score', round(cla_cat_cat['score'][0],4), "1")
    #     cl2.metric('Classe', int(cla_cat_cat['classe'][0]), "1")
    #     cl3.metric('Rank', int(cla_cat_cat['rank'][0]), "1")
    #     cl4.metric('Lucro', int(cla_cat_cat['lucro'][0]), "1")

    #     cl1.metric('Valor Total Comprado', round(base_cat['Sales'].sum(), 2), '1')
    #     cl2.metric('Valor Lucro', round(base_cat['Profit'].sum(), 2), '1')
    #     cl3.metric('Valor Médio Comprado', round(base_cat['Sales'].mean(), 2), '1')
    #     cl4.metric('Quantidade Comprada', round(base_cat['Quantity'].sum(), 2), '1')
    #     with st.expander('Pedidos:'):
    #         st.dataframe(base_cat[['Order Date', 'Sub-Category', 'Product Name', 'Quantity', 'Sales', 'Profit']])


with tabbi:
    st.header('Dados do Business Intelligence')
    with st.expander('Região'):

        # st.dataframe(rg_reg)

        aggr = st.selectbox('Agregador Região', ['sum', 'mean'])
        st.dataframe(rg_reg.pivot_table(index='Region', columns='ano',
                     values='yhat', aggfunc=aggr, fill_value=0))

        # if st.checkbox('Detalhar Região'):
        regiao = st.selectbox('Região:', rg_reg['Region'].unique())
        gr_reg = rg_reg[rg_reg['Region'] == regiao].groupby(
            'ano')['yhat'].sum().reset_index()
        proj = alt.Chart(gr_reg).mark_line(
            color='blue').encode(x='ano', y='yhat')
        gr_base = base[base['Region'] == regiao].groupby(
            'OYear')['Sales'].sum().reset_index()
        real = alt.Chart(gr_base).mark_line(
            color='red').encode(x='OYear', y='Sales')
        st.altair_chart(proj + real)

        if (st.checkbox('Entregas na Região (Mapa):')):
            base_reg = base[base['Region'] == regiao].reset_index()
            coords_reg = base_reg[['Region', 'State', 'City']].copy().drop_duplicates().reset_index()
            coords_reg = coords_reg.merge(
                coords, left_on=['City'], right_on=['cidade'], how='left')
            coords_reg = coords_reg.rename(columns={
                'lng': 'lon'
            })
            coords_reg_undefined = coords_reg[coords_reg['lat'].isna()]
            coords_reg = coords_reg[coords_reg['lat'] > 0]

            st.map(coords_reg)

            if (st.checkbox('Registros não reconhecidos para a Região: ')):
                st.dataframe(
                    coords_reg_undefined[['Region', 'State', 'City', 'lat', 'lon']])

            st.dataframe(base_reg[['Order ID', 'Order Date', 'Ship Date', 'Ship Mode',
                         'Customer ID', 'Customer Name', 'Segment', 'City', 'Sales', 'Profit']])

    with st.expander('Vendas Por Região (Mapa):'):
        coords_vendas_reg = base.groupby('State')['Sales'].sum().reset_index()
        coords_vendas_reg = coords_vendas_reg.merge(estados, left_on=['State'], right_on=['name'], how='left')
        coords_vendas_reg.drop(columns=['name'])

        fig = px.choropleth(coords_vendas_reg,locations='usps',locationmode='USA-states',color='Sales')
        fig.update_layout(title='Vendas por Estado', geo_scope='usa', template="plotly_dark")
        st.plotly_chart(fig)
        

    with st.expander('Segmento'):

        # st.dataframe(rg_seg)

        aggs = st.selectbox('Agregador Segmento', ['sum', 'mean'])
        st.dataframe(rg_seg.pivot_table(index='Segment',
                     columns='ano', values='yhat', aggfunc=aggs, fill_value=0))

        # if st.checkbox('Detalhar Segmento'):
        segmento = st.selectbox('Segmento:', rg_seg['Segment'].unique())
        gr_seg = rg_seg[rg_seg['Segment'] == segmento].groupby(
            'ano')['yhat'].sum().reset_index()
        proj = alt.Chart(gr_seg).mark_line(
            color='blue').encode(x='ano', y='yhat')
        gr_base = base[base['Segment'] == segmento].groupby(
            'OYear')['Sales'].sum().reset_index()
        real = alt.Chart(gr_base).mark_line(
            color='red').encode(x='OYear', y='Sales')
        st.altair_chart(proj + real)

        if (st.checkbox('Entregas do Segmento (Mapa):')):
            base_seg = base[base['Segment'] == segmento].reset_index()
            coords_seg = base_seg[['Region', 'State', 'City']
                                  ].copy().drop_duplicates().reset_index()
            coords_seg = coords_seg.merge(
                coords, left_on=['City'], right_on=['cidade'], how='left')
            coords_seg = coords_seg.rename(columns={
                'lng': 'lon'
            })
            coords_seg_undefined = coords_seg[coords_seg['lat'].isna()]
            coords_seg = coords_seg[coords_seg['lat'] > 0]

            st.dataframe(coords_seg)
            st.map(coords_seg)

            if (st.checkbox('Registros não reconhecidos para o segmento: ')):
                st.dataframe(
                    coords_seg_undefined[['Region', 'State', 'City', 'lat', 'lon']])

            coords_vendas_seg = base_seg.groupby('State')['Sales'].sum().reset_index()
            coords_vendas_seg = coords_vendas_seg.merge(estados, left_on=['State'], right_on=['name'], how='left')
            coords_vendas_seg.drop(columns=['name'])
            fig = px.choropleth(coords_vendas_seg,locations='usps',locationmode='USA-states',color='Sales')
            fig.update_layout(title='Vendas por Estado', geo_scope='usa', template="plotly_dark")
            st.plotly_chart(fig)

            st.dataframe(base_seg[['Order ID', 'Order Date', 'Ship Date', 'Ship Mode',
                         'Customer ID', 'Customer Name', 'Region', 'City', 'Sales', 'Profit']])

with tabstone:
    st.header('Dados do Comércio Eletrônico')
