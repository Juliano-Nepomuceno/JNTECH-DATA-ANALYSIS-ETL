import dash
import dash_bootstrap_components as dbc
from dash import html, page_container, dcc, Input, Output


app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css",
        "https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Poppins:wght@400;600&display=swap"
    ],
    suppress_callback_exceptions=True,
)


app.layout = dbc.Container(
    [
       
        dbc.Row(
    [
        dbc.Col(
            html.H1(
                "JNTECH - ETL / ANALISE DE DADOS",
                style={
                    "padding": "2px 0px",  

                    
                    "fontSize": "30px",
                    "color": "#ffffff",  
                    "backgroundColor": "#007bff", 
                    "border": "5px solid #0056b3",
                    "borderRadius": "15px",
                    "textAlign": "center",
                    "fontFamily": "'Montserrat', sans-serif",
                    "boxShadow": "0px 5px 5px rgba(0, 0, 0, 0.3)",
                },
                id="app-title",
            ),
            width=5,  
             style={
        "marginLeft": "100px", 
    },
        ),
        dbc.Col(
            html.Div(
                dbc.Button(
                    [
                        html.I(className="fab fa-linkedin me-2"),
                        "Linkedin Juliano Nepomuceno",
                    ],
                    href="https://www.linkedin.com/in/juliano-nepomuceno-25753952/",
                    target="_blank",
                    color="primary",
                    style={
                        "marginTop": "15px",
                        "fontFamily": "'Poppins', sans-serif",
                        "fontWeight": "600",
                    },
                ),
                style={"textAlign": "center"},
            ),
            width=3, 
        ),
     dbc.Col(
            html.Div(
                [
                    dbc.Button(
                        [
                            html.I(className="fab fa-github me-2"),
                            "GitHub Juliano Nepomuceno",
                        ],
                        href="https://github.com/Juliano-Nepomuceno",
                        target="_blank",
                        color="dark",
                        style={
                            "fontFamily": "'Poppins', sans-serif",
                            "fontWeight": "600",
                        },
                    ),
                ],
                style={"marginTop": "15px", "textAlign": "center"},
            ),
            width=3,  
        ),
    ],
    style={"marginTop": "30px", "textAlign": "center"},
        
),

        
        dbc.Card(
            dbc.CardBody(
                [
                    
                    dbc.NavbarSimple(
                        children=[
                            dbc.NavLink(
                                dbc.Button(
                                    [
                                        html.I(className="bi bi-bar-chart-fill text-primary me-2"),
                                        "VENDAS",
                                    ],
                                    color="info",
                                    size="lg",
                                    style={"fontFamily": "'Poppins', sans-serif", "fontWeight": "600"},
                                    href="/",
                                )
                            ),
                             dbc.NavLink(
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-chart-line text-info me-2"),
                                        "PREVISÃO DE LUCRO E VENDAS",
                                    ],
                                    color="light",
                                    size="lg",
                                    style={"fontFamily": "'Poppins', sans-serif", "fontWeight": "600"},
                                    href="/previsao",
                                )
                            ),
                            dbc.NavLink(
                                dbc.Button(
                                    [
                                        html.I(className="bi bi-people-fill text-danger me-2"),
                                        "CLIENTES",
                                    ],
                                    color="light",
                                    size="lg",
                                    style={"fontFamily": "'Poppins', sans-serif", "fontWeight": "600"},
                                    href="/clientes",
                                )
                            ),
                            dbc.NavLink(
                                dbc.Button(
                                    [
                                        html.I(className="bi bi-box2-fill text-success me-2"),
                                        "PRODUTOS",
                                    ],
                                    color="light",
                                    size="lg",
                                    style={"fontFamily": "'Poppins', sans-serif", "fontWeight": "600"},
                                    href="/produtos",
                                )
                            ),
                            dbc.NavLink(
                                dbc.Button(
                                    [
                                        html.I(className="bi bi-trophy-fill text-warning me-2"),
                                        "RANK DE VENDEDORES",
                                    ],
                                    color="light",
                                    size="lg",
                                    style={"fontFamily": "'Poppins', sans-serif", "fontWeight": "600"},
                                    href="/vendedores",
                                )
                            ),
                           
                        ],
                        dark=False,
                        color="",
                        style={
                            "borderRadius": "15px",
                            "marginBottom": "30px",
                            "padding": "10px",
                            "justifyContent": "center",
                            "boxShadow": "0px 4px 10px rgba(0, 0, 0, 0.1)",
                            "backgroundColor": "#F0E68C		",  # Cor dourada suave
                        },
                    ),
                   
                    page_container,
                ]
            ),
            style={
                "width": "90%",
                "margin": "auto",
                "padding": "40px",
                "marginTop": "40px",
                "border": "3px solid #0056b3",
                "borderRadius": "25px",
                "boxShadow": "0px 4px 20px rgba(0, 0, 0, 0.2)",
                "backgroundColor": "#ffffff",  
            },
        ),
    ],
    fluid=True,
    style={
        "backgroundColor": "#f7f7f7",  
        "minHeight": "100vh",  
        "padding": "20px",
    },
)


previsao_layout = dbc.Container(
    [
        html.H2("Previsão de Lucro e Vendas", style={"textAlign": "center", "marginBottom": "20px"}),
        dbc.Row(
            dbc.Col(
                html.P(
                    "Aqui você pode visualizar e analisar a previsão de lucro e vendas com base em dados históricos.",
                    style={"textAlign": "center", "fontSize": "18px", "color": "#555"},
                )
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    "Gráficos e análises detalhadas serão exibidos aqui.",
                    style={
                        "textAlign": "center",
                        "border": "2px dashed #007bff",
                        "padding": "20px",
                        "borderRadius": "10px",
                        "color": "#007bff",
                    },
                )
            )
        ),
    ],
    fluid=True,
    style={
        "backgroundColor": "#ffffff",
        "padding": "20px",
        "borderRadius": "15px",
        "boxShadow": "0px 4px 20px rgba(0, 0, 0, 0.1)",
        "marginTop": "30px",
    },
)


app.pages = {
    "/previsao": {
        "layout": previsao_layout,
        "name": "Previsão de Lucro e Vendas",
    }
}

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
