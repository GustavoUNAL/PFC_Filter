import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import xmlrpc.client as xml
import os

model = "example1"
file_type = ".plecs"
plecs = xml.Server("http://localhost:1080/RPC2")

# Simulamos el modelo con plecs
simulation_result = plecs.plecs.simulate(model)
# Obtenemos los tiempos de la simulación
time = simulation_result["Time"]
# Obtenemos los valores de la simulación
value = simulation_result["Values"][0]

# Calculamos la transformada de Fourier
n = len(value)
fft_value = np.fft.fft(value)
frequencies = np.fft.fftfreq(n, d=(time[1] - time[0]))
# Solo tomamos la parte positiva de las frecuencias y amplitudes
positive_frequencies = frequencies[:n//2]
positive_amplitudes = np.abs(fft_value[:n//2])
# Creamos los gráficos
# Gráfico de la señal en función del tiempo
fig_time = go.Figure(data=go.Scatter(x=time, y=value, mode='lines', name='Señal en el tiempo'))
# Gráfico de la transformada de Fourier
fig_fft = go.Figure(data=go.Scatter(x=positive_frequencies, y=positive_amplitudes, mode='lines', name='Transformada de Fourier'))




# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout de la aplicación
app.layout = html.Div(children=[
    html.H1(children='Análisis de Señal'),

    html.Div(children='''
        Filtro de armónicos activo.
    '''),

    html.Div(children=[
        html.H2(children='Señal en el Tiempo'),
        dcc.Graph(
            id='time-graph',
            figure=fig_time
        ),
    ]),

    html.Div(children=[
        html.H2(children='Transformada de Fourier'),
        dcc.Graph(
            id='fft-graph',
            figure=fig_fft
        ),
    ]),
])

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
