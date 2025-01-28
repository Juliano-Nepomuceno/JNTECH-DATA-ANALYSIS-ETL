import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from urllib.parse import unquote
import oracledb
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from databaseconnection import connectionoracle


dash.register_page(__name__, path_template="/estatisticaproduto/<produto>")


layout = html.Div([
        dbc.Row([
     
        dbc.Col(html.P("Exportar para", style={"fontSize": "20px", "color": "blue"}), width=2),
       
        dbc.Col(
            html.Div(
                [
                    html.Div("Excel", className="text-center mb-2"),  
                    html.A(
                        html.I(className="fa fa-file-excel"),  
                        id="export-excel-statistics-produto",
                        download="tabela_produtos.xlsx",  
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
                        id="export-csv-statistics-produto",
                        download="tabela_produtos.csv",  
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
    dcc.Location(id='url', refresh=False),  
    html.Div(id='conteudo-produto'),  
    dcc.Graph(id='grafico-produtos')  
])


@dash.callback(
    [Output('conteudo-produto', 'children'),
     Output('grafico-produtos', 'figure')],
    Input('url', 'pathname') 
)
def exibir_conteudo(pathname):
    if pathname.startswith('/estatisticaproduto/'):  
        try:
            
            parts = pathname.split("/")
            produto_name = unquote(parts[-1])

            
            connection = connectionoracle()
            
            
            query = f"""
            select  trunc(datesale) as data_da_venda, products.name as nome_do_produto 
            from sales
            inner join products 
            on sales.products_fk = products.id
            where products.name = :produto_name

            """
            
            
            df = pd.read_sql(query, con=connection, params={"produto_name": produto_name})
            
            connection.close() 
            print(df)
            
            if df.empty:
                return (
                    html.Div([
                        html.H1(f"Vendedor: {produto_name.capitalize()}"),
                        html.P("Nenhum dado encontrado para este vendedor.")
                    ]),
                    px.line().update_layout(title="Sem dados disponíveis")
                )

           
            fig = px.line(
                df,
                x="DATA_DA_VENDA",  
                y="NOME_DO_PRODUTO",     
                title=f"Vendas do produto: {produto_name.capitalize()}",
                labels={"NOME_DO_PRODUTO": "Produto", "TOTAL_vendas": "Total de compras"},
                color="NOME_DO_PRODUTO",  
            )

            return (
                html.Div([
                    html.H1(f"Estatísticas do produto: {produto_name.capitalize()}"),
                    html.P(f"Você está visualizando as estatísticas para o vendedor: {produto_name}")
                ]),
                fig
            )
        except Exception as e:
            
            return (
                html.Div([
                    html.H1("Erro ao carregar dados"),
                    html.P(f"Detalhes do erro: {str(e)}")
                ]),
                px.bar().update_layout(title="Erro ao carregar gráfico")
            )
    else:
        # 
        return (
            html.Div([
                html.H1("404 - Página Não Encontrada"),
                html.P("A URL digitada não corresponde a nenhuma página válida ok.")
            ]),
            px.bar().update_layout(title="Página não encontrada")
        )
    
def export_csv():
    csv_string = df.to_csv(index=False)
    b64_csv = base64.b64encode(csv_string.encode()).decode()
    return f"data:text/csv;base64,{b64_csv}"

def export_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Vendas")
    b64_excel = base64.b64encode(output.getvalue()).decode()
    return f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}"


def export_pdf():
    html_table = df.to_html(index=False)
    html_content = f"<html><body>{html_table}</body></html>"
    
    
    pdf_file = pdfkit.from_string(html_content, False)
    b64_pdf = base64.b64encode(pdf_file).decode()
    return f"data:application/pdf;base64,{b64_pdf}"


def update_pdf(vendedor_name):
    return export_pdf()

@dash.callback(
    Output('export-excel-statistics-produto', 'href'),
    Input('vendedor-input', 'value')
)
def update_excel(vendedor_name):
    return export_excel()

@dash.callback(
    Output('export-csv-statistics-produto', 'href'),
    Input('vendedor-input', 'value')
)
def update_csv(vendedor_name):
    return export_csv()
