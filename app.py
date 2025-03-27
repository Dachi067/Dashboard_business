import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash.dash_table import DataTable

# Charger les données depuis un fichier CSV
data = pd.read_csv('data/business_data.csv')

# Créer une figure de graphique à barres des revenus par mois
fig = px.bar(data, x='Mois', y='Revenus', title='Revenus par mois')

# Créer une figure de graphique à lignes des revenus (pour afficher la tendance)
fig_line = px.line(data, x='Mois', y='Revenus', title='Tendance des revenus')

# Calculer la croissance des revenus par rapport au mois précédent
data['Croissance'] = data['Revenus'].pct_change() * 100

# Créer l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Définir la mise en page de l'application
app.layout = dbc.Container([
    html.H1('Dashboard Business', className='text-center my-4'),
    
    # Première ligne avec les KPI (Revenus totaux et Croissance des revenus)
    dbc.Row([
        dbc.Col(html.H2(f"Revenus totaux : {data['Revenus'].sum():,.2f} €"), width=6),
        dbc.Col(html.H2(f"Croissance des revenus : {data['Croissance'].iloc[-1]:,.2f}%"), width=6),
    ], className='my-4'),
    
    # Deuxième ligne avec un filtre pour sélectionner le mois
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': month} for month in data['Mois'].unique()],
            value=data['Mois'].unique()[0],  # Valeur initiale
            multi=False
        ), width=6),
    ], className='my-4'),
    
    # Troisième ligne avec les graphiques
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig), width=6),
        dbc.Col(dcc.Graph(figure=fig_line), width=6),
    ]),
    
    # Quatrième ligne avec un tableau de données interactif
    dbc.Row([
        dbc.Col(DataTable(
            id='data-table',
            columns=[{"name": col, "id": col} for col in data.columns],
            data=data.to_dict('records'),
            style_table={'height': '300px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '5px'},
            style_header={'fontWeight': 'bold', 'backgroundColor': '#f1f1f1'},
        ), width=12)
    ])
])

# Callback pour mettre à jour le graphique en fonction du mois sélectionné
@app.callback(
    dash.dependencies.Output('month-dropdown', 'value'),
    [dash.dependencies.Input('month-dropdown', 'value')]
)
def update_graph(selected_month):
    filtered_data = data[data['Mois'] == selected_month]
    fig = px.bar(filtered_data, x='Mois', y='Revenus', title=f'Revenus pour {selected_month}')
    return fig

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
