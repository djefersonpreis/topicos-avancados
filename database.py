import pandas as pd
import streamlit as st
import datetime as dt

@st.cache
def load_database():
    item = pd.read_excel('base/item.xlsx')
    pedido = pd.read_excel('base/pedido.xlsx')
    produto = pd.read_excel('base/produto.xlsx')
    subcategoria = pd.read_excel('base/subcategoria.xlsx')
    categoria = pd.read_excel('base/categoria.xlsx')
    consumidor = pd.read_excel('base/consumidor.xlsx')
    segmento = pd.read_excel('base/segmento.xlsx')
    cidade = pd.read_excel('base/cidade.xlsx')
    pais = pd.read_excel('base/pais.xlsx')
    mercado = pd.read_excel('base/mercado.xlsx')
    regiao = pd.read_excel('base/regiao.xlsx')
    item = item.drop(columns=['Unnamed: 0'])
    pedido = pedido.drop(columns=['Unnamed: 0'])
    produto = produto.drop(columns=['Unnamed: 0'])
    subcategoria = subcategoria.drop(columns=['Unnamed: 0'])
    categoria = categoria.drop(columns=['Unnamed: 0'])
    consumidor = consumidor.drop(columns=['Unnamed: 0'])
    segmento = segmento.drop(columns=['Unnamed: 0'])
    cidade = cidade.drop(columns=['Unnamed: 0'])
    pais = pais.drop(columns=['Unnamed: 0'])
    mercado = mercado.drop(columns=['Unnamed: 0'])
    regiao = regiao.drop(columns=['Unnamed: 0'])
    df_gs = item.merge(pedido, on='ped_codigo', how='left')
    df_gs = df_gs.merge(produto, on='pro_codigo', how='left')
    df_gs = df_gs.merge(subcategoria, on='sub_codigo', how='left')
    df_gs = df_gs.merge(categoria, on='cat_codigo', how='left')
    df_gs = df_gs.merge(consumidor, on='con_codigo', how='left')
    df_gs = df_gs.merge(segmento, on='seg_codigo', how='left')
    df_gs = df_gs.merge(cidade, on='cid_codigo', how='left')
    df_gs = df_gs.merge(pais, on='pai_codigo', how='left')
    df_gs = df_gs.merge(regiao, on='reg_codigo', how='left')
    df_gs = df_gs.merge(mercado, on='mer_codigo', how='left')
    df_gs = df_gs.rename(
        columns={
            'descricao_x': 'categoria',
            'descricao_y': 'segmento',
            'descricao': 'mercado'
        }
    )
    df_gs['ano'] = df_gs['data_pedido'].dt.year
    df_gs['mes'] = df_gs['data_pedido'].dt.month
    df_gs['data_pedido'] = df_gs['data_pedido'].dt.date
    A07_cli = pd.read_feather('base/A07_cli.feather')
    A08_mer = pd.read_feather('base/A08_mer.feather')
    A08_mer['ano'] = A08_mer['ds'].dt.year
    A08_mer['mes'] = A08_mer['ds'].dt.month
    A08_reg = pd.read_feather('base/A08_reg.feather')
    A08_reg['ano'] = A08_reg['ds'].dt.year
    A08_reg['mes'] = A08_reg['ds'].dt.month
    A09_pai = pd.read_feather('base/A09_pai.feather')
    A10_pai = pd.read_feather('base/A10_pai.feather')
    A11_pai = pd.read_feather('base/A11_pai.feather')
    A11_pro = pd.read_feather('base/A11_pro.feather')
    a11_pro = A11_pro.merge(produto, left_on='vizinho', right_on='pro_codigo', how='left')
    A11_sub = pd.read_feather('base/A11_sub.feather')
    A12_pai = pd.read_feather('base/A12_pai.feather')
    return df_gs, A07_cli, A09_pai, A10_pai, A11_pai, A08_mer, A08_reg, A12_pai, a11_pro, A11_sub
