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

# Creamos un DataFrame con 'time' y 'value'
df = pd.DataFrame({'Time': time, 'Value': value})

# Definimos el tiempo de muestreo
sampling_time = 1e-6

# Realizamos la Transformada de Fourier
fft_values = np.fft.fft(df['Value'])

# Obtenemos las frecuencias para el eje x teniendo en cuenta el tiempo de muestreo
frequencies = np.fft.fftfreq(len(df['Value']), d=sampling_time)

# Calculamos la amplitud de la señal
amplitude = np.abs(fft_values)

# Creamos un DataFrame con las frecuencias y la amplitud
fft_df = pd.DataFrame({'Frequency': frequencies, 'Amplitude': amplitude})

# Filtramos el DataFrame para solo tener las frecuencias positivas y menores a 1000 Hz
positive_fft_df = fft_df[(fft_df['Frequency'] > 0) & (fft_df['Frequency'] <= 1000)]

# Ajustamos la amplitud para reflejar el número total de puntos y el hecho de que estamos usando la mitad del espectro
positive_fft_df['Amplitude'] = 2 * positive_fft_df['Amplitude'] / len(df['Value'])

# Creamos los gráficos
# Gráfico de la señal en función del tiempo
fig_time = go.Figure(data=go.Scatter(x=time, y=value, mode='lines', name='Señal en el tiempo'))

# Gráfico de la transformada de Fourier
fig_fft = go.Figure(data=go.Scatter(x=positive_fft_df['Frequency'], y=positive_fft_df['Amplitude'], mode='lines', name='Transformada de Fourier'))
fig_fft.update_layout(xaxis=dict(range=[0, 1000]))

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Definir el layout de la aplicación
app.layout = html.Div(children=[
    html.H1(children='Análisis de Señal'),

    html.Div(children='''
        Señal original con armónicos y su transformada de Fourier.
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
