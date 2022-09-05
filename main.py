import pandas as pd

import streamlit as st
import altair as alt

from database import load_database

st.title('Projeto TAV')

gs, cla_cli, prb_pai, clu_pai, knn_pai, reg_mer, reg_reg, out_pai, knn_pro, knn_sub = load_database()

#st.dataframe(gs)

opcao = st.sidebar.selectbox(
    'Informação: ',
    [
        'ERP',
        'BI',
        'eStore'
    ]
)

if opcao == 'ERP':
    consumidor = st.sidebar.selectbox(
        'Selecione o consumidor: ',
        gs['con_codigo'].unique() 
    )
    gs_cli = gs[gs['con_codigo'] == consumidor].reset_index()
    #st.dataframe(gs_cli)
    cla_con = cla_cli[cla_cli['con_codigo'] == consumidor].reset_index()
    #st.dataframe(cla_con)  
    prb_con = prb_pai[prb_pai['pai_codigo'] == cla_con['pai_codigo'][0]].reset_index()
    #st.dataframe(prb_con)
    clu_con = clu_pai[clu_pai['referencia'] == cla_con['pai_codigo'][0]].reset_index()
    #st.dataframe(clu_con)
    gs_cli_pais_nome = gs_cli['pais'][0]
    knn_con = knn_pai[knn_pai['referencia'] == gs_cli_pais_nome].reset_index()
    #st.dataframe(knn_con)
    st.dataframe(gs_cli[['cliente_codigo','cliente_nome','segmento']].drop_duplicates())
    cl1, cl2, cl3, cl4, cl5, cl6 = st.columns(6)
    with cl1:
        st.metric('Score', round(cla_con['score'][0],4), "1")
    with cl2:
        st.metric('Classe', int(cla_con['classe'][0]), "1")
    with cl3:
        st.metric('Rank', int(cla_con['rank'][0]), "1")
    with cl4:
        st.metric('Lucro', int(cla_con['lucro'][0]), "1")
    with cl5:
        st.metric('Probabilidade de Lucro', round(prb_con['lucro_1'][0],4), "1")
    with cl6:
        st.metric('Cluster', int(clu_con['cluster'][0]), "1")
    with st.expander('Pedidos'):
        st.dataframe(gs_cli[['pedido_numero','data_pedido','produto_nome','subcategoria','categoria','quantidade','valor_bruto','valor_lucro']])
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric('Lucro Total', round(gs_cli['valor_lucro'].sum(),2), "1")
    with col2:
        st.metric('Vendas Total', round(gs_cli['valor_bruto'].sum(),2), "1")
    with col3:
        st.metric('Média Lucro', round(gs_cli['valor_lucro'].mean(),2), "1")
    with col4:
        st.metric('Média Itens', round(gs_cli['valor_bruto'].mean(),2), "1")
    with col5:
        st.metric('Quantidade', int(gs_cli['valor_lucro'].count()), "1")
    with col6:
        st.metric('Média Desconto', round(gs_cli['desconto'].mean(),2), "1")
    with st.expander('dados de mercado'):
        st.dataframe(gs_cli[['cidade','estado','pais','regiao','mercado']].drop_duplicates())
        st.dataframe(cla_con[['zpai_codigo','zcid_codigo','zmer_codigo','zreg_codigo',
                                'zvalor_bruto','zvalor_lucro','zquantidade','zvalor_entrega']])
        m1, m2, m3 = st.columns(3)
        with m1:
            st.write('RFM - País')
            st.dataframe(clu_con[['f_lucro_x','f_vendas_x','m_entrega_x','m_lucro_x','m_qtde_x','m_vendas_x','r_dias_x']].transpose())
        with m2:
            st.write('RFM - Cluster')
            st.dataframe(clu_con[['f_lucro_y','f_vendas_y','m_entrega_y','m_lucro_y','m_qtde_y','m_vendas_y','r_dias_y']].transpose())
        with m3:         
            st.write('Países similares')
            st.dataframe(knn_con)

elif opcao == 'BI':
    with st.expander('Mercado'):
        aggm = st.selectbox('Agregador Mercado', ['sum', 'mean'])
        st.dataframe(reg_mer.pivot_table(index='mercado', columns='ano', values='yhat', aggfunc=aggm, fill_value=0))
        if st.checkbox('Detalhar mercado'):
            merc = st.selectbox('Mercado:', reg_mer['mercado'].unique())
            gr_merc = reg_mer[reg_mer['mercado'] == merc].groupby('ano')['yhat'].mean().reset_index()
            proj = alt.Chart(gr_merc).mark_line(color='blue').encode(x='ano', y='yhat')
            gr_gs = gs[gs['mercado'] == merc].groupby('ano')['valor_bruto'].mean().reset_index()
            real = alt.Chart(gr_gs).mark_line(color='red').encode(x='ano', y='valor_bruto')
            st.altair_chart(proj + real)
        if st.checkbox('Detalhar Ano - Mercado'):
            anom = st.selectbox('Ano:', reg_mer['ano'].unique())
            st.dataframe(reg_mer[reg_mer['ano'] == anom].pivot_table(
                index='mercado', columns='mes', values='yhat', aggfunc=aggm, fill_value=0
            ))
    with st.expander('Regiao'):
        aggr = st.selectbox('Agregador Região', ['sum', 'mean'])
        st.dataframe(reg_reg.pivot_table(index='regiao', columns='ano', values='yhat', aggfunc=aggr, fill_value=0))
        if st.checkbox('Detalhar região'):
            reg = st.selectbox('Região:', reg_reg['regiao'].unique())
            gr_reg = reg_reg[reg_reg['regiao'] == reg].groupby('ano')['yhat'].mean().reset_index()
            proj = alt.Chart(gr_reg).mark_line(color='blue').encode(x='ano', y='yhat')
            gr_gs = gs[gs['regiao'] == reg].groupby('ano')['valor_bruto'].mean().reset_index()
            real = alt.Chart(gr_gs).mark_line(color='red').encode(x='ano', y='valor_bruto')
            st.altair_chart(proj + real)
        if st.checkbox('Detalhar Ano - Região'):
            anom = st.selectbox('Ano:', reg_reg['ano'].unique())
            st.dataframe(reg_reg[reg_reg['ano'] == anom].pivot_table(
                index='regiao', columns='mes', values='yhat', aggfunc=aggr, fill_value=0
            ))
    with st.expander('RFM/Outliers'):    
        out_paises = st.multiselect('Paises:', gs['pais'].unique())
        st.dataframe(out_pai[out_pai['referencia'].isin(out_paises)])
elif opcao == 'eStore':
    consumidor = st.sidebar.selectbox(
        'Selecione o consumidor: ',
        gs['con_codigo'].unique() 
    )
    gs_cli = gs[gs['con_codigo'] == consumidor][['pro_codigo','produto_nome', 'subcategoria']].reset_index()
    #st.dataframe(gs_cli)

    for index, row in gs_cli.iterrows():
        st.info('{0}({1})'.format(row['produto_nome'],row['pro_codigo']))
        #st.dataframe(knn_pro[knn_pro['referencia'] == row['pro_codigo']])
        st.write('Similares')
        for idx, rw in knn_pro[knn_pro['referencia'] == row['pro_codigo']].iterrows():
            st.success('{0}({1})'.format(rw['produto_nome'],rw['pro_codigo']))

    for subcategoria in gs_cli['subcategoria'].unique():
        st.info(subcategoria)
        #st.dataframe(knn_sub[knn_sub['referencia'] == subcategoria])
        st.warning('Similares')
        for idx, rw in knn_sub[knn_sub['referencia'] == subcategoria].iterrows():
            st.error(rw['vizinho'])
    if st.checkbox('Não clique aqui'):
        st.balloons()        

