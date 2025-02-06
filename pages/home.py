import dash
from dash import html, dcc, Input, Output, register_page
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from databaseconnection import connectionoracle
import dash_table
from io import BytesIO
import base64

# Registrar a página
register_page(__name__, path="/")

connection = connectionoracle()
queryalldata = """
                SELECT sales.id AS numero_da_nota, 
                       sales.datesale AS data, 
                       products.name AS nome_do_produto, 
                       sellers.name AS nome_do_vendedor, 
                       clients.name AS nome_do_cliente 
                FROM sales
                INNER JOIN products ON sales.products_fk = products.id
                INNER JOIN sellers ON sales.sellers_fk = sellers.id
                INNER JOIN clients ON sales.clients_fk = clients.id
            """
dfalldata = pd.read_sql(queryalldata, con=connection)

# Layout da página
layout = html.Div([
    dcc.Store(id='store-dataframe'),  # Armazenamento do DataFrame
    dcc.Store(id='store-figura'),  # Armazenamento do gráfico

    dbc.Row([
        dbc.Col(html.H1("Tabela Vendas", style={"text-align": "center"}), width=3),
        
        dbc.Col(
            dcc.Dropdown(
                id="tipo_selecao",
                options=[
                    {"label": "Total Vendas por data", "value": "vendas"},
                    {"label": "Total de Lucro por data", "value": "lucro"},
                ],
                value="vendas",
                style={
                    "width": "100%",
                    "margin": "auto",
                    "padding": "3px, 5px",
                    "borderRadius": "15px",
                    "boxShadow": "0 2px 7px rgba(0, 0, 0, 0.1)",
                    "backgroundColor": "#f1f3f5",
                    "fontWeight": "bold",
                    "color": "#495057",
                    "fontSize": "21px",
                    "border": "3px solid #F0E68C",
                    "boxSizing": "border-box",
                },
                className="custom-dropdown",
            ),
            width=3,
        ),
        dbc.Col( html.Div(
                [
                    html.Div("Tabela completa", className="text-center mb-2", style={"fontSize": "20px"}),  
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
        dbc.Col(html.Div("Exportar para", className="text-center mb-2", style={"fontSize": "25px"})),
        # Colunas separadas para cada ícone de exportação
        dbc.Col(
            html.A(
                html.I(className="fa fa-file-pdf"),  # Ícone PDF
                id="export-pdf",
                style={"fontSize": "50px", "color": "red", "cursor": "pointer"}
            ),
            width=1,
            className="text-center",
        ),
        
        dbc.Col(
            html.A(
                html.I(className="fa fa-file-excel"),  # Ícone Excel
                id="export-excel",
                style={"fontSize": "50px", "color": "green", "cursor": "pointer"}
            ),
            width=1,
            className="text-center",
        ),
        
        dbc.Col(
            html.A(
                html.I(className="fa fa-file-csv"),  # Ícone CSV
                id="export-csv",
                style={"fontSize": "50px", "color": "orange", "cursor": "pointer"}, 
            ),
            width=1,
            className="text-center",
        ),
    ]),

    dbc.Row(
        dbc.Col(
            dcc.Graph(
                id="grafico_principal",
                figure=px.line().update_layout(title="Carregando gráfico...")  # Placeholder
            ),
            width=12,
        )
    ),

    # Componente para download de Excel
    dcc.Download(id="download-dataframe-xlsx"),

    # Componente para download de CSV
    dcc.Download(id="download-dataframe-csv"),

    # Componente para download de PDF do gráfico
    dcc.Download(id="download-graph-pdf"),
])

# Callback para atualizar o gráfico
@dash.callback(
    [Output('grafico_principal', 'figure'),
     Output('store-dataframe', 'data'),
     Output('store-figura', 'data')],  # Armazenar a figura
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
            return px.line().update_layout(title="Opção inválida"), None, None

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
                    font=dict(size=17),
                    bgcolor="lightblue",
                    activecolor="blue",
                ),
            ),
            height=400,
            width=1200,
            xaxis_title="Data",
            yaxis_title=titulo,
        )

        return fig, dfalldata.to_dict("records"), fig.to_dict()  # Usar dfalldata

    except Exception as e:
        return px.line().update_layout(title=f"Erro: {e}"), None, None

# Callback para exportar o gráfico como PDF
@dash.callback(
    Output("download-graph-pdf", "data"),
    Input("export-pdf", "n_clicks"),
    Input('store-figura', 'data'),  # Recuperar a figura
    prevent_initial_call=True
)
def exportar_pdf_grafico(n_clicks, stored_figure):
    if n_clicks and stored_figure:
        # Criar a figura a partir do dicionário armazenado
        fig = go.Figure(stored_figure)  # Usando go.Figure em vez de px.line.from_dict
        
        # Salvar o gráfico como PDF
        fig.write_image("grafico_vendas.pdf")
        return dcc.send_file("grafico_vendas.pdf")

# Callbacks para exportação para CSV e Excel
@dash.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-csv", "n_clicks"),
    Input('store-dataframe', 'data'),
    prevent_initial_call=True,
)
def exportar_csv(n_clicks, stored_data):
    if n_clicks and stored_data:
        df = pd.DataFrame(dfalldata)  # Usar dfalldata
        return dcc.send_data_frame(df.to_csv, "dados_vendas.csv", index=False)

@dash.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("export-excel", "n_clicks"),
    Input('store-dataframe', 'data'),
    prevent_initial_call=True,
)
def exportar_excel(n_clicks, stored_data):
    if n_clicks and stored_data:
        df = pd.DataFrame(dfalldata)  # Usar dfalldata
        return dcc.send_data_frame(df.to_excel, "dados_vendas.xlsx", index=False)
