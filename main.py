import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
import os

# Ruta al archivo CSV
file_path = 'test.csv'

# Crear la aplicación Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Análisis de Fourier de la Señal'),

    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Intervalo de actualización en milisegundos (cada 5 segundos)
        n_intervals=0
    ),

    dcc.Graph(id='signal-graph'),
    dcc.Graph(id='harmonics-graph'),
    html.H3(id='thd-output', style={'color': 'blue'})
])

def compute_fft(file_path):
    # Cargar los datos desde un archivo CSV
    data = pd.read_csv(file_path)

    # Filtrar los datos desde time >= 0.9667
    data = data[data['Time'] >= 0.9667]

    # Extraer los datos filtrados
    time = data['Time']
    signal = pd.to_numeric(data['Am2:Measured current'], errors='coerce').dropna()

    # Convertir la señal a un array de NumPy para evitar problemas de alineación
    signal_array = np.array(signal)

    # Calcular la frecuencia de muestreo real (fs)
    fs = 1 / (time.iloc[1] - time.iloc[0])  # Frecuencia de muestreo en Hz

    # Realizar la FFT
    N = len(signal_array)
    yf = fft(signal_array)
    xf = fftfreq(N, 1/fs)[:N//2]
    harmonics = 2.0/N * np.abs(yf[:N//2])

    # Ajustar las frecuencias para que el primer armónico corresponda a 60 Hz
    # Encontrar la frecuencia del primer pico y escalar
    index_of_max = np.argmax(harmonics[1:]) + 1  # Ignorar el componente en DC (0 Hz)
    scaling_factor = 60 / xf[index_of_max]
    xf_scaled = xf * scaling_factor

    # Filtrar los armónicos hasta 200 Hz
    filter_mask = xf_scaled <= 200
    xf_filtered = xf_scaled[filter_mask]
    harmonics_filtered = harmonics[filter_mask]

    # Identificar el armónico correspondiente a 60 Hz después del escalado
    fundamental_index = np.argmin(np.abs(xf_scaled - 60))
    fundamental_amplitude = harmonics[fundamental_index]

    # Calcular el THD (Total Harmonic Distortion)
    thd = np.sqrt(np.sum(harmonics[fundamental_index+1:]**2)) / fundamental_amplitude
    thd_percentage = thd * 100

    return time, signal_array, xf_filtered, harmonics_filtered, thd_percentage

@app.callback(
    [Output('signal-graph', 'figure'),
     Output('harmonics-graph', 'figure'),
     Output('thd-output', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n_intervals):
    time, signal_array, xf_filtered, harmonics_filtered, thd_percentage = compute_fft(file_path)

    signal_fig = {
        'data': [
            go.Scatter(x=time, y=signal_array, mode='lines', name='Señal en el tiempo')
        ],
        'layout': go.Layout(
            title='Señal en el tiempo',
            xaxis={'title': 'Tiempo (s)'},
            yaxis={'title': 'Amplitud'},
            hovermode='closest'
        )
    }

    harmonics_fig = {
        'data': [
            go.Bar(x=xf_filtered, y=harmonics_filtered, name='Harmónicos')
        ],
        'layout': go.Layout(
            title='Análisis de Fourier (Harmónicos)',
            xaxis={'title': 'Frecuencia (Hz)'},
            yaxis={'title': 'Amplitud'},
            hovermode='closest'
        )
    }

    thd_text = f"THD: {thd_percentage:.2f}%"

    return signal_fig, harmonics_fig, thd_text

if __name__ == '__main__':
    app.run_server(debug=True)
