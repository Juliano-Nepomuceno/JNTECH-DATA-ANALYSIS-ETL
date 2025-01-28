import dash
from dash import dcc, html
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import oracledb
import io
import base64
import pandas as pd
import pdfkit
from databaseconnection import connectionoracle


dash.register_page(__name__, path="/exibicao")


layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("Exibição de Tabelas", style={"text-align": "center"}), width=12),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id="dropdown-tabelas",
                options=[
                    {"label": "Tabela de Vendas", "value": "sales"},
                    {"label": "Tabela de Vendedores", "value": "sellers"},
                    {"label": "Tabela de Clientes", "value": "clients"},
                    {"label": "Tabela de Produtos", "value": "products"},
                ],
                value="sales",  
                style={"width": "50%", "margin": "auto", "padding": "10px"},
            ),
            width=12,
        )
    ]),
    dbc.Row([
        dbc.Col(
            html.Div(
                id="table-output",
                style={"padding": "20px"}
            ),
            width=12
        ),
    ])
])

# Callback para atualizar a tabela
@dash.callback(
    Output('table-output', 'children'),
    Input('dropdown-tabelas', 'value')
)
def update_table(selected_table):
    try:
        
        connection = connectionoracle()

       
        if selected_table == "sales":
            query = """
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
        else:
            query = f"SELECT * FROM {selected_table}"

        df = pd.read_sql(query, con=connection)
        connection.close()  

        
        if selected_table != "sales":
            df.columns = [col.replace("_", " ").capitalize() for col in df.columns]

        
        table = dbc.Table.from_dataframe(
            df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            style={"textAlign": "center"}
        )
        return table

    except Exception as e:
        return html.Div(f"Erro ao carregar os dados: {e}", style={"color": "red", "text-align": "center"})
