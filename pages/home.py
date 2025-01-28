import dash
from dash import html, dcc, Input, Output, register_page
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import oracledb
from databaseconnection import connectionoracle

# Registrar a página
register_page(__name__, path="/")




layout = html.Div([
   
    dbc.Row([
        dbc.Col(html.H1("Tabela Vendas", style={"text-align": "center"}), width=3),  # Primeira coluna
        
        dbc.Col(
            dcc.Dropdown(
                id="tipo_selecao",
                options=[
                    {"label": "Total Vendas por data", "value": "vendas"},
                    {"label": "Total de Lucro por data", "value": "lucro"},
                ],
                value="vendas",  
                style={"width": "50%", "margin": "auto", "padding": "20px"},
            ), 
            width=8,
            
            ),
        dbc.Col( html.Div(
                [
                    html.Div("Tabela completa", className="text-center mb-2"),  
                    html.A(
                        html.I(className="fa fa-table"),  
                        id="export-pdf",
                        href="/tabelavendas",  
                        
                        style={"fontSize": "70px", "color": "blue"}  
                    ),
                ],
                className="text-center",
            ),
            width=1,
        ),
         
    ]),
    
   

    dbc.Row(
        dbc.Col(
            dcc.Graph(
                id="grafico_principal",
                figure=px.line().update_layout(title="Carregando gráfico...")  
            ),
            width=12,
        )
    ),
])

# Callback para atualizar o gráfico
@dash.callback(
    Output('grafico_principal', 'figure'),
    Input('tipo_selecao', 'value')
)
def update_grafico(tipo_selecao):
    try:
        # Conectar ao banco de dados
        connection = connectionoracle()

        
        if tipo_selecao == "vendas":
            query = """
            SELECT trunc(datesale) AS data_da_venda, COUNT(*) AS total_vendas
            FROM sales
            GROUP BY TRUNC(datesale)
            """
            coluna_y = "TOTAL_VENDAS"
            titulo = "Total de Vendas"
        elif tipo_selecao == "lucro":
            query = """
            SELECT trunc(datesale) AS data_da_venda, SUM(products.price) AS total_lucro
            FROM sales
            INNER JOIN products ON sales.products_fk = products.id
            GROUP BY TRUNC(datesale)
            ORDER BY total_lucro DESC
            """
            coluna_y = "TOTAL_LUCRO"
            titulo = "Total de Lucro"
        else:
            return px.line().update_layout(title="Opção inválida")

        
        df = pd.read_sql(query, con=connection)
        connection.close()  # Fechar a conexão

        # Criar o gráfico
        fig = px.line(df, x="DATA_DA_VENDA", y=coluna_y, title=titulo)
        fig.update_layout(
            autosize=True,
            xaxis=dict(
                rangeslider=dict(visible=True),
                rangeselector=dict(
                    buttons=[
                        {"count": 1, "label": "Último Mês", "step": "month", "stepmode": "backward"},
                        {"count": 3, "label": "Últimos 3 Meses", "step": "month", "stepmode": "backward"},
                        {"count": 6, "label": "Últimos 6 Meses", "step": "month", "stepmode": "backward"},
                        {"count": 12, "label": "Últimos 12 Meses", "step": "month", "stepmode": "backward"},
                        {"step": "all", "label": "Todos os Dados"},
                    ],
                    font=dict(size=17),  # Tamanho da fonte dos botões
                    bgcolor="lightblue",  # Cor de fundo dos botões
                    activecolor="blue",  # Cor do botão ativo
                ),
            ),
            height=400,
            width=1200,
            xaxis_title="Data",
            yaxis_title=titulo,
        )

        return fig
    except Exception as e:
        return px.line().update_layout(title=f"Erro: {e}")
