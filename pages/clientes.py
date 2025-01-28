import dash
from dash import html
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import oracledb
import dash_bootstrap_components as dbc
from databaseconnection import connectionoracle



dash.register_page(__name__, path="/clientes")




# Conectar ao banco
clientes = "clients.id"
connection = connectionoracle()

 

query = f"select clients.name as nome_do_cliente, COUNT(*) AS total_compras from clients inner join sales on sales.clients_fk = {clientes} GROUP BY clients.id, clients.name ORDER BY  total_compras DESC"



df = pd.read_sql(query, con=connection)

print(df.head())


fig = px.bar(
   df,
    x='NOME_DO_CLIENTE', 
    y='TOTAL_COMPRAS', 
    title="Numero de Compras", 
)


connection.close()

dash.register_page(__name__, path="/clientes")  # Página inicial



layout = html.Div([
    
   
        dbc.Row(
            [
                dbc.Col( html.Div(
                [
                    html.Div("Tabela completa", className="text-center mb-2"),  
                    html.A(
                        html.I(className="fa fa-table"), 
                        id="export-pdf",
                        href="/tabelaclientes",  
                        
                        style={"fontSize": "70px", "color": "blue"}  
                    ),
                ],
                className="text-center",
            ),
            width=1,
        ),
            ],
            justify="center",
            className="mb-4",
        ),
         
        dbc.Row(
            dbc.Col(html.Div(id="output-date-range"), width=6),
            justify="center",
        ),
        
    html.H1("Tabela Clientes"),
    
    dcc.Graph(figure=fig),

])
