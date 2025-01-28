import dash
from dash import html, dcc, Input, Output, register_page
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import oracledb
from databaseconnection import connectionoracle
from sklearn.linear_model import LinearRegression
import numpy as np


register_page(__name__, path="/previsao", title="Previsão de Vendas")


layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("Previsão de Vendas", style={"text-align": "center"}), width=3),  
        
        dbc.Col(
            dcc.Dropdown(
                id="tipo_previsao",
                options=[
                    {"label": "Total Vendas", "value": "vendas"},
                    {"label": "Total Lucro", "value": "lucro"},
                ],
                value="vendas", 
                style={"width": "50%", "margin": "auto", "padding": "20px"},
            ), 
            width=8,
        ),
    ]),
    
    dbc.Row(
        dbc.Col(
            dcc.Graph(
                id="grafico_previsao",
                figure=px.line().update_layout(title="Carregando gráfico...")  # Gráfico inicial vazio
            ),
            width=12,
        )
    ),
])

# Função para realizar a previsão com regressão linear
def realizar_previsao(df, tipo_previsao):
    # Definir o modelo de regressão linear
    model = LinearRegression()

    
    df["data_timestamp"] = pd.to_datetime(df["DATA_DA_VENDA"]).astype(np.int64) // 10**9  # Convertendo para timestamp
    
   
    if tipo_previsao == "vendas":
        X = df[["data_timestamp"]]  
        y = df["TOTAL_VENDAS"]     
    else:
        X = df[["data_timestamp"]]  
        y = df["TOTAL_LUCRO"]      

    model.fit(X, y)
    
    # Fazer previsões para os próximos 12 meses (exemplo)
    previsao_futura = pd.DataFrame({
        "data_da_venda": pd.date_range(df["DATA_DA_VENDA"].max() + pd.Timedelta(days=1), periods=12, freq='M')
    })
    previsao_futura["data_timestamp"] = previsao_futura["data_da_venda"].astype(np.int64) // 10**9
    previsao_futura["previsao"] = model.predict(previsao_futura[["data_timestamp"]])
    
    return previsao_futura

# Callback para atualizar o gráfico da previsão
@dash.callback(
    Output('grafico_previsao', 'figure'),
    Input('tipo_previsao', 'value')
)
def update_previsao(tipo_previsao):
    try:
        
        connection = connectionoracle()

        
        if tipo_previsao == "vendas":
            query = """
            SELECT trunc(datesale) AS data_da_venda, COUNT(*) AS TOTAL_VENDAS
            FROM sales
            GROUP BY TRUNC(datesale)
            """
            coluna_y = "TOTAL_VENDAS"
            titulo = "Total de Vendas"
        elif tipo_previsao == "lucro":
            query = """
            SELECT trunc(datesale) AS data_da_venda, SUM(products.price) AS TOTAL_LUCRO
            FROM sales
            INNER JOIN products ON sales.products_fk = products.id
            GROUP BY TRUNC(datesale)
            ORDER BY TOTAL_LUCRO DESC
            """
            coluna_y = "TOTAL_LUCRO"
            titulo = "Total de Lucro em R$"
        else:
            return px.line().update_layout(title="Opção inválida")

       
        df = pd.read_sql(query, con=connection)
        connection.close()  

       
        df["DATA_DA_VENDA"] = pd.to_datetime(df["DATA_DA_VENDA"])

      
        previsao_df = realizar_previsao(df, tipo_previsao)

    
        fig = px.line(previsao_df, x="data_da_venda", y="previsao", title=f"Previsão de {titulo}")

        
        fig.add_scatter(x=previsao_df["data_da_venda"], 
                        y=previsao_df["previsao"], 
                        mode="lines", 
                        name="Previsão", 
                        line=dict(dash='dash', color='red')) 

        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(visible=True),
                rangeselector=dict(
                    buttons=[] 
                ),
            ),
           
            autosize=True,
            xaxis_title="Data",
            yaxis_title=f"{titulo} Previsto",
        )

        return fig
    except Exception as e:
        return px.line().update_layout(title=f"Erro: {e}")
