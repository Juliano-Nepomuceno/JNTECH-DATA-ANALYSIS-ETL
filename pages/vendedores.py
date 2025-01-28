
import dash
from dash import html, dcc
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import io
import base64
from databaseconnection import connectionoracle

dash.register_page(__name__, path="/vendedores")


connection = connectionoracle()

query = """
select sellers.name as nome_do_vendedor, COUNT(*) AS total_vendas 
from sales 
inner join sellers on sales.sellers_fk = sellers.id
GROUP BY sellers.name
ORDER BY total_vendas DESC
"""

df = pd.read_sql(query, con=connection)


table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)


layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("Rank de Vendedores")),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div("Exportar como Excel", style={"textAlign": "center", "marginBottom": "5px"}),
            html.A(
                html.I(className="fa fa-file-excel", style={"fontSize": "50px", "color": "green"}),
                id="export-excel-seller-rank",
                download="tabela_rank_vendedores.xlsx",
                href="",  
                target="_blank"
            )
        ], width=2, style={"textAlign": "center"}),
        dbc.Col([
            html.Div("Exportar como CSV", style={"textAlign": "center", "marginBottom": "5px"}),
            html.A(
                html.I(className="fas fa-file-alt", style={"fontSize": "50px", "color": "blue"}),
                id="export-csv-seller-rank",
                download="tabela_rank_vendedores.csv",
                href="", 
                target="_blank"
            )
        ], width=2, style={"textAlign": "center"}),
    ], justify="center"),
    dbc.Row(dbc.Col(html.Div(table)))
])

# Funções para exportação
def export_excel(dataframe):
    """Exporta o DataFrame como arquivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Vendas')
    output.seek(0)
    encoded = base64.b64encode(output.read()).decode()
    return f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded}"

def export_csv(dataframe):
    """Exporta o DataFrame como arquivo CSV."""
    csv_string = dataframe.to_csv(index=False, encoding='utf-8')
    b64 = base64.b64encode(csv_string.encode()).decode()
    return f"data:text/csv;charset=utf-8;base64,{b64}"

# Callbacks para exportação
@dash.callback(
    Output('export-excel-seller-rank', 'href'),
    Input('export-excel-seller-rank', 'n_clicks'),
    prevent_initial_call=True
)
def update_excel(n_clicks):
    return export_excel(df)

@dash.callback(
    Output('export-csv-seller-rank', 'href'),
    Input('export-csv-seller-rank', 'n_clicks'),
    prevent_initial_call=True
)
def update_csv(n_clicks):
    return export_csv(df)
