import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

# Charger les données depuis un fichier CSV
data = pd.read_csv('data/business_data.csv')

# Ajouter une colonne pour la croissance des revenus
data['Croissance'] = data['Revenus'].pct_change() * 100

# Créer les graphiques initiaux
fig_bar = px.bar(data, x='Mois', y='Revenus', title='Revenus par mois')
fig_line = px.line(data, x='Mois', y='Revenus', title='Tendance des revenus')

# Créer une application Dash avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

# Layout du Dashboard
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Dashboard Business",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-4"
    ),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Revenus Totaux", className="card-title"),
                html.H2(f"{data['Revenus'].sum():,.2f} €", className="card-text")
            ])
        ], color="success", inverse=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Croissance Moyenne", className="card-title"),
                html.H2(f"{data['Croissance'].mean():.2f} %", className="card-text")
            ])
        ], color="info", inverse=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Mois avec le plus haut revenu", className="card-title"),
                html.H2(f"{data.loc[data['Revenus'].idxmax(), 'Mois']}", className="card-text")
            ])
        ], color="warning", inverse=True), width=4),
    ], className="mb-4"),

    # Filtres
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': month} for month in data['Mois']],
            value=data['Mois'].unique()[0],
            multi=True,
            placeholder="Sélectionner le(s) mois..."
        ), width=6),

        dbc.Col(dcc.DatePickerRange(
            id='date-picker',
            start_date=data['Mois'].iloc[0],
            end_date=data['Mois'].iloc[-1],
            display_format='MMM YYYY'
        ), width=6)
    ], className="mb-4"),

    # Graphiques
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart', figure=fig_bar), width=6),
        dbc.Col(dcc.Graph(id='line-chart', figure=fig_line), width=6)
    ], className="mb-4"),

    # Tableau de données interactif
    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id='data-table',
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.to_dict('records'),
            style_table={'height': '400px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '5px'},
            style_header={'backgroundColor': '#007bff', 'color': 'white'},
            sort_action='native',
            filter_action='native',
            row_selectable='multi'
        ), width=12)
    ]),

    # Bouton d'exportation
    dbc.Row([
        dbc.Col(dbc.Button("Exporter en CSV", id="btn-export", color="primary", className="mt-3"), width=3)
    ])
])

# Callback pour filtrer les données par mois
@app.callback(
    Output('bar-chart', 'figure'),
    Output('line-chart', 'figure'),
    Input('month-dropdown', 'value')
)
def update_graph(selected_months):
    if not selected_months:
        filtered_data = data
    else:
        filtered_data = data[data['Mois'].isin(selected_months)]

    fig_bar = px.bar(filtered_data, x='Mois', y='Revenus', title='Revenus par mois')
    fig_line = px.line(filtered_data, x='Mois', y='Revenus', title='Tendance des revenus')

    return fig_bar, fig_line

# Callback pour exporter le fichier CSV
@app.callback(
    Output('data-table', 'data'),
    Input('btn-export', 'n_clicks'),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    path = 'data/exported_data.csv'
    data.to_csv(path, index=False)
    print(f"Fichier exporté : {path}")
    return data.to_dict('records')

# Lancer le serveur
if __name__ == '__main__':
    app.run(debug=True)

