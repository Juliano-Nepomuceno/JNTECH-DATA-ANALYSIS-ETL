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

# Registro da página secundária
dash.register_page(__name__, path="/tabelaclientes")

# Conexão com o banco de dados Oracle
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

# Remove espaços em branco ao redor dos nomes das colunas
df.columns = df.columns.str.strip()

# Adiciona ações (exemplo de botão) para cada linha
df['Estatisticas individuais Cliente'] = df['NOME_DO_CLIENTE'].apply(
    lambda x: html.Div(
        dbc.Button(
            [html.I(className="fas fa-chart-line me-2", style={'font-size': '50px', 'color': 'blue'}),  # Ícone com a classe Font Awesome
             f" {x}"],  # Texto do botão com o nome do vendedor
            color="info",  # Cor do botão
            class_name="me-1",  # Classe adicional (margem)
            href=f"/estatisticacliente/{x}",  # Link dinâmico baseado no número da nota
            target="_blank"  # Abrir em nova aba
        )
    )
)

# Funções para exportação de dados

# Função para exportar dados como CSV
def export_csv():
    csv_string = df.to_csv(index=False)
    b64_csv = base64.b64encode(csv_string.encode()).decode()
    return f"data:text/csv;base64,{b64_csv}"

# Função para exportar dados como Excel
def export_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Vendas")
    b64_excel = base64.b64encode(output.getvalue()).decode()
    return f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}"





layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("Estatísticas Individuais Filtro por Cliente"), width=5),
        dbc.Col(html.P("Exportar para", style={"fontSize": "20px", "color": "blue"}), width=2),
       
       
        dbc.Col(
            html.Div(
                [
                    html.Div("Excel", className="text-center mb-2"),  
                    html.A(
                        html.I(className="fa fa-file-excel"), 
                        id="export-excel-client",
                        download="tabela_vendas.xlsx",  
                        href="#",  
                        target="_blank",  
                        style={"fontSize": "50px", "color": "green"} 
                    ),
                ],
                className="text-center",
            ),
            width=1,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div("CSV", className="text-center mb-2"),  
                    html.A(
                        html.I(className="fas fa-file-alt"),  
                        id="export-csv-client",
                        download="tabela_vendas.csv", 
                        href="#",  
                        target="_blank",  
                        style={"fontSize": "50px", "color": "blue"}  
                    ),
                ],
                className="text-center",
            ),
            width=1,
        ),
    ]),

   
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='client-input',
                type='text',
                placeholder='Digite o nome do vendedor...',
                debounce=False,  
                style={'width': '100%', "height": "50px", "borderRadius": "15px", "borderColor": "blue", "borderWidth": "3px"},
            )
        ], width=5)
    ]),

    
    dbc.Row([
        dbc.Col([
            dbc.Table(id='clients-table', striped=True, bordered=True, hover=True)
        ], width=12)
    ])
])

# Callback para atualizar a tabela com base no nome do vendedor
@dash.callback(
    Output('clients-table', 'children'),
    [Input('client-input', 'value')]
)
def update_table(cliente_name):
    # Filtra os dados com base no nome do vendedor
    if cliente_name is None or cliente_name == '':
        filtered_df = df  
    else:
        filtered_df = df[df['NOME_DO_CLIENTE'].str.contains(cliente_name, case=False, na=False)]
    
    
    table_header = [
        html.Thead(html.Tr([html.Th(col) for col in filtered_df.columns]))
    ]
    
   
    table_body = [
        html.Tbody([html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns]) for i in range(len(filtered_df))])
    ]
    
    return table_header + table_body 


@dash.callback(
    Output('export-pdf-client', 'href'),
    Input('client-input-client', 'value')
)

@dash.callback(
    Output('export-excel-client', 'href'),
    Input('client-input', 'value')
)
def update_excel(vendedor_name):
    return export_excel()

@dash.callback(
    Output('export-csv-client', 'href'),
    Input('client-input', 'value')
)
def update_csv(vendedor_name):
    return export_csv()