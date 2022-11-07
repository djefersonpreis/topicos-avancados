import pandas as pd
import streamlit as st
import altair as alt

st.title('App - Tópicos Avançados')

@st.cache 
def load_database():
    return pd.read_feather('database/GS.feather'), \
        pd.read_feather('database/classificacaoz_consumidor.feather'), \
        pd.read_feather('database/clusterizacao_pais.feather'), \
        pd.read_feather('database/regressao_mercado.feather'), \
        pd.read_feather('database/regressao_regiao.feather'), \
        pd.read_feather('database/knn_pais.feather'), \
        pd.read_feather('database/knn_produto.feather'), \
        pd.read_feather('database/knn_subcategoria.feather'), \
        pd.read_feather('database/outliers_pais.feather'), \
        pd.read_feather('database/probabilidade_pais.feather'), \
        pd.read_feather('database/localizacao.feather')
    
gs, cla_con, clu_pai, reg_mer, reg_reg, knn_pais, knn_pro, knn_sub, out_pai, prb_pai, coords = load_database()

rg_mer = reg_mer.copy()
rg_mer['ano'] = rg_mer['ds'].dt.year

rg_reg = reg_reg.copy()
rg_reg['ano'] = rg_reg['ds'].dt.year

# st.dataframe(gs) 
# st.dataframe(cla_con) 

taberp, tabbi, tabstone = st.tabs(['Sistema Interno', 'Gestão', 'E-Commerce'])

with taberp:
    st.header('Dados do Sistema Interno')
    consumidor = st.selectbox('Selecione o Consumidor', gs['Customer ID'].unique())
    gs_con = gs[gs['Customer ID'] == consumidor].reset_index()
    # st.dataframe(gs_con)
    cla_con_con = cla_con[cla_con['Customer ID'] == consumidor].reset_index()
    # st.dataframe(cla_con_con) 

    st.dataframe(knn_pais)
    with st.expander('Países similares'):
        st.write(gs_con['Country'][0])
        st.dataframe(knn_pais[knn_pais['referencia'] == gs_con['Country'][0]]) 
        st.write('Probabilidade:')
        st.dataframe(prb_pai[prb_pai['Country'] == gs_con['Country'][0]])

    st.dataframe(gs_con[['Customer Name', 'Segment']].drop_duplicates())
    cl1, cl2, cl3, cl4 = st.columns(4)
    cl1.metric('Score', round(cla_con_con['score'][0],4), "1")
    cl2.metric('Classe', int(cla_con_con['classe'][0]), "1")
    cl3.metric('Rank', int(cla_con_con['rank'][0]), "1")
    cl4.metric('Lucro', int(cla_con_con['lucro'][0]), "1")

    cl1.metric('Valor Total Comprado', round(gs_con['Sales'].sum(), 2), '1')
    cl2.metric('Valor Lucro', round(gs_con['Profit'].sum(), 2), '1')
    cl3.metric('Valor Médio Comprado', round(gs_con['Sales'].mean(), 2), '1')
    cl4.metric('Quantidade Comprada', round(gs_con['Quantity'].sum(), 2), '1')
    with st.expander('Pedidos:'):
        st.dataframe(gs_con[['Order Date', 'Product Name', 'Quantity', 'Sales', 'Profit']])
    
    clu_pai_cli = clu_pai[clu_pai['reference'] == gs_con['Country'].values[0]]
    st.dataframe(clu_pai_cli[['cluster', 'm_deliver', 'm_profit', 'm_sales', 'm_quantity', 'f_sales', 'f_profit', 'r_days']])
    st.dataframe(clu_pai_cli[['cluster', 'clm_deliver', 'clm_profit', 'clm_saless', 'clm_quantity', 'clf_sales', 'clf_profit', 'clr_days']])

    ## TODO: MAPA com as coordenadas do cliente


with tabbi:
    st.header('Dados do Business Intelligence')
    with st.expander('Mercado'):
        aggm = st.selectbox('Agregador Mercado', ['sum', 'mean'])
        st.dataframe(rg_mer.pivot_table(index='Market', columns='ano', values='yhat', aggfunc=aggm, fill_value=0))
    

        if st.checkbox('Detalhar mercado'):
            mercado = st.selectbox('Mercado:', rg_mer['Market'].unique())
            gr_mer = rg_mer[rg_mer['Market'] == mercado].groupby('ano')['yhat'].sum().reset_index()
            proj = alt.Chart(gr_mer).mark_line(color='blue').encode(x='ano', y='yhat')
            gr_gs = gs[gs['Market'] == mercado].groupby('OYear')['Sales'].sum().reset_index()
            real = alt.Chart(gr_gs).mark_line(color='red').encode(x='OYear', y='Sales')
            st.altair_chart(proj + real)

    with st.expander('Região'):
        aggr = st.selectbox('Agregador Região', ['sum', 'mean'])
        st.dataframe(rg_reg.pivot_table(index='Region', columns='ano', values='yhat', aggfunc=aggr, fill_value=0))
    

        if st.checkbox('Detalhar Região'):
            regiao = st.selectbox('Região:', rg_reg['Region'].unique())
            gr_reg = rg_reg[rg_reg['Region'] == regiao].groupby('ano')['yhat'].sum().reset_index()
            proj = alt.Chart(gr_reg).mark_line(color='blue').encode(x='ano', y='yhat')
            gr_gs = gs[gs['Region'] == regiao].groupby('OYear')['Sales'].sum().reset_index()
            real = alt.Chart(gr_gs).mark_line(color='red').encode(x='OYear', y='Sales')
            st.altair_chart(proj + real)

    with st.expander('RFM/Outliers'):
        out_pais = st.multiselect('Países:', gs_con['Country'].unique())
        st.dataframe(out_pai[out_pai['referencia'].isin(out_pais)])


    # st.dataframe(reg_mer)
    # st.dataframe(reg_reg)


    ## TODO: MAPA dos mercados, das regiões e dos países 


with tabstone:
    st.header('Dados do Comércio Eletrônico')
    consumidor = st.selectbox('Selecione o Consumidor: ', gs['Customer ID'].unique())
    gs_cli = gs[gs['Customer ID'] == consumidor][['Product ID', 'Product Name', 'Sub-Category']].reset_index()
    # st.dataframe(gs_cli)
    for subcategoria in gs_cli['Sub-Category'].unique():
        st.info(subcategoria)
        st.warning('Similares')
        for idx, rw in knn_sub[knn_sub['referencia'] == subcategoria].iterrows():
            st.error(rw['vizinho'])
    for index, row in gs_cli.iterrows():
        st.info('{0}({1})'.format(row['Product Name'], row['Product ID']))
        st.warning('Similares')
        for idx, rw in knn_pro[knn_pro['referencia'] == row['Product Name']].iterrows():
            st.error(rw['vizinho'])


