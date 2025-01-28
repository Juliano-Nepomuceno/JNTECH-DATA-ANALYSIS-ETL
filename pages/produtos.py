import dash
from dash import html
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
import oracledb
import dash_bootstrap_components as dbc
from databaseconnection import connectionoracle



dash.register_page(__name__, path="/produtos")




# Conectar ao banco
produtos = "products.id"
connection = connectionoracle()

 

query = f"""select products.name as nome_do_produto, COUNT(*) AS total_vendas 
from sales 
inner join products on sales.products_fk = products.id
GROUP BY products.id, products.name 
ORDER BY  total_vendas DESC"""




df = pd.read_sql(query, con=connection)

print(df.head())




fig = px.bar(
   df,
    x='NOME_DO_PRODUTO', 
    y='TOTAL_VENDAS', 
    title="NUMERO DE VENDAS", 
)


connection.close()

dash.register_page(__name__, path="/produtos") 



layout = html.Div([

        dbc.Row(
            [
                dbc.Col( html.Div(
                [
                    html.Div("Tabela completa", className="text-center mb-2"),  
                    html.A(
                        html.I(className="fa fa-table"),  
                        id="export-pdf",
                        href="/tabelaprodutos",  
                        
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
        
    html.H1("Tabela Produtos"),
    
    dcc.Graph(figure=fig),

])