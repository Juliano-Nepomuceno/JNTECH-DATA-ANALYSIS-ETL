import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from urllib.parse import unquote
import oracledb
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from databaseconnection import connectionoracle



dash.register_page(__name__, path_template="/estatisticavendedor/<vendedor>")


layout = html.Div([
        dbc.Row([
     
        dbc.Col(html.P("Exportar para", style={"fontSize": "20px", "color": "blue"}), width=2),
       
        dbc.Col(
            html.Div(
                [
                    html.Div("PDF", className="text-center mb-2"), 
                    html.A(
                        html.I(className="fa fa-file-pdf"), 
                        id="export-pdf-statistics",
                        download="tabela_vendas.pdf", 
                        href="#", 
                        target="_blank",  #
                        style={"fontSize": "50px", "color": "red"}  
                    ),
                ],
                className="text-center",
            ),
            width=1,
        ),
        dbc.Col(
            html.Div(
                [
                    html.Div("Excel", className="text-center mb-2"), 
                    html.A(
                        html.I(className="fa fa-file-excel"),  
                        id="export-excel-statistics",
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
                        id="export-csv-statistics",
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
    dcc.Location(id='url', refresh=False),  
    html.Div(id='conteudo'),  
    dcc.Graph(id='grafico-vendas')  
])


@dash.callback(
    [Output('conteudo', 'children'),
     Output('grafico-vendas', 'figure')],
    Input('url', 'pathname')  
)
def exibir_conteudo(pathname):
    if pathname.startswith('/estatisticavendedor/'):  
        try:
           
            parts = pathname.split("/")
            vendedor_name = unquote(parts[-1])

            
            connection = connectionoracle()
            
            
            query = f"""
            SELECT 
                sellers.name AS nome_do_vendedor, 
                COUNT(*) AS total_vendas
            FROM 
                sellers
            INNER JOIN 
                sales 
            ON 
                sales.sellers_fk = sellers.id
            WHERE 
                sellers.name = :vendedor_name
            GROUP BY 
                sellers.name
            ORDER BY 
                total_vendas DESC
            """
            
            
            df = pd.read_sql(query, con=connection, params={"vendedor_name": vendedor_name})
            connection.close()  

            
            if df.empty:
                return (
                    html.Div([
                        html.H1(f"Vendedor: {vendedor_name.capitalize()}"),
                        html.P("Nenhum dado encontrado para este vendedor.")
                    ]),
                    px.bar().update_layout(title="Sem dados disponíveis")
                )

            
            fig = px.bar(
                df,
                x="NOME_DO_VENDEDOR",  # Coluna para o eixo X
                y="TOTAL_VENDAS",      # Coluna para o eixo Y
                title=f"Vendas do Vendedor: {vendedor_name.capitalize()}",
                labels={"NOME_DO_VENDEDOR": "Vendedor", "TOTAL_VENDAS": "Total de Vendas"},
                color="NOME_DO_VENDEDOR",  # Diferencia por cor
            )

            return (
                html.Div([
                    html.H1(f"Estatísticas do Vendedor: {vendedor_name.capitalize()}"),
                    html.P(f"Você está visualizando as estatísticas para o vendedor: {vendedor_name}")
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
        
        return (
            html.Div([
                html.H1("404 - Página Não Encontrada"),
                html.P("A URL digitada não corresponde a nenhuma página válida.")
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

@dash.callback(
    Output('export-pdf-statistics', 'href'),
    Input('vendedor-input', 'value')
)
def update_pdf(vendedor_name):
    return export_pdf()

@dash.callback(
    Output('export-excel-statistics', 'href'),
    Input('vendedor-input', 'value')
)
def update_excel(vendedor_name):
    return export_excel()

@dash.callback(
    Output('export-csv-statistics', 'href'),
    Input('vendedor-input', 'value')
)
def update_csv(vendedor_name):
    return export_csv()
