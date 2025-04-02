import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import seasonal_decompose

# Charger les données
data = pd.read_csv('data/business_data.csv')
data['Croissance'] = data['Revenus'].pct_change() * 100

# Préparer les données pour la régression
X = np.array(range(len(data))).reshape(-1, 1)
y = data['Revenus'].values.reshape(-1, 1)
model = LinearRegression()
model.fit(X, y)
data['Prédiction'] = model.predict(X)

# Détection d'anomalies
iso_forest = IsolationForest(contamination=0.1)
data['Anomalie'] = iso_forest.fit_predict(data[['Revenus']])
data['Anomalie'] = data['Anomalie'].map({1: 'Normal', -1: 'Anomalie'})

# Analyse des tendances saisonnières
decomposition = seasonal_decompose(data['Revenus'], model='additive', period=12)

# Initialisation de l'application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Layout avec sidebar
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("📊 Dashboard Business", className="text-center text-primary"),
            html.Hr(),
            dbc.Nav([
                dbc.NavLink("Accueil", href="#", active=True, className="mb-2"),
                dbc.NavLink("Analyse des revenus", href="#", className="mb-2"),
                dbc.NavLink("Anomalies", href="#", className="mb-2"),
                dbc.NavLink("Tendances", href="#", className="mb-2"),
            ], vertical=True, pills=True),
        ], width=2, className="bg-light p-3"),

        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Revenus Totaux"),
                    html.H2(f"{data['Revenus'].sum():,.2f} €", className="text-success")
                ])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Croissance Moyenne"),
                    html.H2(f"{data['Croissance'].mean():.2f} %", className="text-info")
                ])), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H4("Anomalies Détectées"),
                    html.H2(f"{(data['Anomalie'] == 'Anomalie').sum()}", className="text-danger")
                ])), width=4),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id='bar-chart'), width=6),
                dbc.Col(dcc.Graph(id='line-chart'), width=6),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='anomaly-chart'), width=6),
                dbc.Col(dcc.Graph(id='seasonal-chart'), width=6),
            ])
        ], width=10)
    ])
])

# Callbacks pour les graphiques
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('anomaly-chart', 'figure'),
     Output('seasonal-chart', 'figure')],
    Input('bar-chart', 'clickData')
)
def update_graphs(_):
    fig_bar = px.bar(data, x='Mois', y='Revenus', color='Anomalie', title='Revenus par Mois')
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=data['Mois'], y=data['Revenus'], mode='lines', name='Revenus'))
    fig_line.add_trace(go.Scatter(x=data['Mois'], y=data['Prédiction'], mode='lines', line=dict(dash='dot', color='red'), name='Prédictions'))
    fig_anomaly = px.scatter(data, x='Mois', y='Revenus', color='Anomalie', title='Détection d’anomalies')
    fig_seasonal = go.Figure()
    fig_seasonal.add_trace(go.Scatter(x=data['Mois'], y=decomposition.trend, mode='lines', name='Tendance'))
    fig_seasonal.add_trace(go.Scatter(x=data['Mois'], y=decomposition.seasonal, mode='lines', name='Saisonnalité'))
    return fig_bar, fig_line, fig_anomaly, fig_seasonal

if __name__ == '__main__':
    app.run(debug=True)
