import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Charger les données
data = pd.read_csv('data/business_data.csv')

# Créer une figure avec Plotly
fig = px.bar(data, x='Mois', y='Revenus', title='Revenus par mois')

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Définir la mise en page du tableau de bord
app.layout = html.Div(children=[
    html.H1(children='Dashboard Business'),

    html.Div(children='''
        Analyse des performances mensuelles.
    '''),

    # Affichage du KPI
    html.Div(children=[
        html.H2(f"Revenus totaux : {data['Revenus'].sum()} €", style={'color': 'green'}),
    ], style={'margin-bottom': '20px'}),

    # Affichage du graphique
    dcc.Graph(
        id='revenus-par-mois',
        figure=fig
    )
])

# Lancer le serveur local
if __name__ == '__main__':
  app.run(debug=True)

