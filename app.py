import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.seasonal import seasonal_decompose
import seaborn as sns
import matplotlib.pyplot as plt

# Charger les données depuis un fichier CSV
data = pd.read_csv('data/business_data.csv')

# ➡️ Créer une colonne de croissance des revenus
data['Croissance'] = data['Revenus'].pct_change() * 100

# ➡️ Préparer les données pour la régression linéaire
X = np.array(range(len(data))).reshape(-1, 1)
y = data['Revenus'].values.reshape(-1, 1)

# ➡️ Créer un modèle de régression linéaire
model = LinearRegression()
model.fit(X, y)

# ➡️ Prédiction des revenus
data['Prédiction'] = model.predict(X)

# ➡️ Détection d'anomalies avec Isolation Forest
iso_forest = IsolationForest(contamination=0.1)
data['Anomalie'] = iso_forest.fit_predict(data[['Revenus']])
data['Anomalie'] = data['Anomalie'].map({1: 'Normal', -1: 'Anomalie'})

# ➡️ Analyse des tendances saisonnières
decomposition = seasonal_decompose(data['Revenus'], model='additive', period=12)

# ➡️ Créer une application Dash avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

# ➡️ Layout du Dashboard
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="Dashboard Business - Analyse Avancée",
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
                html.H4("Anomalies Détectées", className="card-title"),
                html.H2(f"{(data['Anomalie'] == 'Anomalie').sum()}", className="card-text")
            ])
        ], color="danger", inverse=True), width=4)
    ], className="mb-4"),

    # Graphiques principaux
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart'), width=6),
        dbc.Col(dcc.Graph(id='line-chart'), width=6)
    ]),

    # Graphique d'anomalies
    dbc.Row([
        dbc.Col(dcc.Graph(id='anomaly-chart'), width=6),
        dbc.Col(dcc.Graph(id='seasonal-chart'), width=6)
    ])
])

# ➡️ Callback pour mettre à jour les graphiques
@app.callback(
    Output('bar-chart', 'figure'),
    Output('line-chart', 'figure'),
    Output('anomaly-chart', 'figure'),
    Output('seasonal-chart', 'figure'),
    Input('bar-chart', 'clickData')
)
def update_graphs(_):
    # ➡️ Bar chart des revenus par mois
    fig_bar = px.bar(
        data,
        x='Mois',
        y='Revenus',
        color='Anomalie',
        title='Revenus par Mois (Anomalies Incluses)'
    )

    # ➡️ Ligne de tendance + prédictions
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=data['Mois'],
        y=data['Revenus'],
        mode='lines',
        name='Revenus réels'
    ))
    fig_line.add_trace(go.Scatter(
        x=data['Mois'],
        y=data['Prédiction'],
        mode='lines',
        line=dict(dash='dot', color='red'),
        name='Prédictions'
    ))
    fig_line.update_layout(title="Tendance des revenus (avec prédictions)")

    # ➡️ Graphique d'anomalies
    fig_anomaly = px.scatter(
        data,
        x='Mois',
        y='Revenus',
        color='Anomalie',
        title='Détection d’anomalies',
        size_max=10
    )

    # ➡️ Graphique de tendance saisonnière
    fig_seasonal = go.Figure()
    fig_seasonal.add_trace(go.Scatter(
        x=data['Mois'],
        y=decomposition.trend,
        mode='lines',
        name='Tendance'
    ))
    fig_seasonal.add_trace(go.Scatter(
        x=data['Mois'],
        y=decomposition.seasonal,
        mode='lines',
        name='Saisonnalité'
    ))
    fig_seasonal.update_layout(title="Analyse des tendances saisonnières")

    return fig_bar, fig_line, fig_anomaly, fig_seasonal


# ➡️ Lancer le serveur
if __name__ == '__main__':
    app.run(debug=True)
