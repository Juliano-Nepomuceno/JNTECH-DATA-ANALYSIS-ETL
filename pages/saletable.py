import dash
from dash import dcc, html
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import oracledb
import io
import base64
import plotly.express as px
import pdfkit
from databaseconnection import connectionoracle


dash.register_page(__name__, path="/tabelavendas")


connection = connectionoracle()
query = """
    select  sales.id as numero_da_nota, sales.datesale as data, products.name as nome_do_produto,
            sellers.name as nome_do_vendedor, clients.name as nome_do_cliente
    from sales
    inner join products on sales.products_fk = products.id
    inner join sellers on sales.sellers_fk = sellers.id
    inner join clients on sales.clients_fk = clients.id
"""
df = pd.read_sql(query, con=connection)


df.columns = df.columns.str.strip()


df['Estatisticas individuais vendedor'] = df['NOME_DO_VENDEDOR'].apply(
    lambda x: html.Div(
        dbc.Button(
            [html.I(className="fas fa-chart-line me-2", style={'font-size': '50px', 'color': 'blue'}),  # Ícone com a classe Font Awesome
             f" {x}"],  
            color="info",  
            href=f"/estatisticavendedor/{x}",  # Link dinâmico baseado no número da nota
            target="_blank"  
        )
    )
)


# Funções para exportação de dados
def export_csv(filtered_df):
    csv_string = filtered_df.to_csv(index=False)
    b64_csv = base64.b64encode(csv_string.encode()).decode()
    return f"data:text/csv;base64,{b64_csv}"


def export_excel(filtered_df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Vendas")
    b64_excel = base64.b64encode(output.getvalue()).decode()
    return f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}"


def export_pdf(filtered_df):
    html_table = filtered_df.to_html(index=False)

    
    fig = px.bar(filtered_df, x="NOME_DO_PRODUTO", y="NUMERO_DA_NOTA", title="Vendas por Produto")
    fig.write_image("grafico.png")

    
    html_content = f"""
    <html>
        <head><title>Relatório de Vendas</title></head>
        <body>
            <h1>Relatório de Vendas</h1>
            {html_table}
            <img src="grafico.png" width="600">
        </body>
    </html>
    """

    
    pdf_file = pdfkit.from_string(html_content, False)
    b64_pdf = base64.b64encode(pdf_file).decode()
    return f"data:application/pdf;base64,{b64_pdf}"



layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("Estatísticas Individuais - Filtro por Vendedor"), width=6),
        dbc.Col(html.P("Exportar para", style={"fontSize": "20px", "color": "blue"}), width=2),
        
        dbc.Col(
            html.A(
                html.I(className="fa fa-file-excel", style={"fontSize": "50px", "color": "green"}),
                id="export-excel",
                download="tabela_vendas.xlsx",
                href="#",
                target="_blank"
            ), width=1
        ),
        dbc.Col(
            html.A(
                html.I(className="fas fa-file-alt", style={"fontSize": "50px", "color": "blue"}),
                id="export-csv",
                download="tabela_vendas.csv",
                href="#",
                target="_blank"
            ), width=1
        ),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='vendedor-input',
                type='text',
                placeholder='Digite o nome do vendedor...',
                style={'width': '100%', "height": "50px", "borderRadius": "15px", "borderColor": "blue", "borderWidth": "3px"},
            )
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Table(id='sales-table', striped=True, bordered=True, hover=True)
        ], width=12)
    ])
])


# Callback para atualizar a tabela com base no nome do vendedor
@dash.callback(
    Output('sales-table', 'children'),
    [
        Input('vendedor-input', 'value')
    ]
)
def update_table(vendedor_name):
    # Filtra os dados com base no nome do vendedor
    if not vendedor_name:
        filtered_df = df
    else:
        filtered_df = df[df['NOME_DO_VENDEDOR'].str.contains(vendedor_name, case=False, na=False)]

   
    table_header = [html.Thead(html.Tr([html.Th(col) for col in filtered_df.columns]))]

   
    table_body = [html.Tbody([html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns]) for i in range(len(filtered_df))])]

    return table_header + table_body


# Callbacks para exportar os dados
@dash.callback(
    Output('export-pdf', 'href'),
    [Input('vendedor-input', 'value')]
)
def update_pdf(vendedor_name):
    filtered_df = df[df['NOME_DO_VENDEDOR'].str.contains(vendedor_name, case=False, na=False)] if vendedor_name else df
    return export_pdf(filtered_df)


@dash.callback(
    Output('export-excel', 'href'),
    [Input('vendedor-input', 'value')]
)
def update_excel(vendedor_name):
    filtered_df = df[df['NOME_DO_VENDEDOR'].str.contains(vendedor_name, case=False, na=False)] if vendedor_name else df
    return export_excel(filtered_df)


@dash.callback(
    Output('export-csv', 'href'),
    [Input('vendedor-input', 'value')]
)
def update_csv(vendedor_name):
    filtered_df = df[df['NOME_DO_VENDEDOR'].str.contains(vendedor_name, case=False, na=False)] if vendedor_name else df
    return export_csv(filtered_df)
