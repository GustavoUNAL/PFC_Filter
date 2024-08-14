import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Ruta del archivo CSV
csv_file = 'test.csv'

# Configuración inicial de la figura y el gráfico
fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'r-', animated=True)

# Lee el CSV para obtener el rango total de tiempo
df = pd.read_csv(csv_file)
time_max = df['Time'].max()

# Duración de la ventana de tiempo en segundos
window_duration = 0.016  # 16 milisegundos

# Función de inicialización
def init():
    ax.set_xlim(0, window_duration)  # Ajusta el límite del eje x para la ventana de tiempo
    ax.set_ylim(df['Sine Wave3'].min(), df['Sine Wave3'].max())  # Ajusta el límite del eje y basado en los datos
    return ln,

# Función de actualización
def update(frame):
    global xdata, ydata  # Asegura que xdata y ydata sean variables globales
    
    # Leer sólo una porción de datos
    chunk_size = 2000  # Número de filas por chunk
    skiprows = frame * chunk_size + 1  # Saltar la primera fila con nombres de columna y los chunks anteriores
    df_chunk = pd.read_csv(csv_file, skiprows=skiprows, nrows=chunk_size, names=['Time', 'Sine Wave3'], header=None)
    
    df_chunk['Time'] = pd.to_numeric(df_chunk['Time'], errors='coerce')
    df_chunk['Sine Wave3'] = pd.to_numeric(df_chunk['Sine Wave3'], errors='coerce')

    xdata.extend(df_chunk['Time'].dropna())
    ydata.extend(df_chunk['Sine Wave3'].dropna())
    
    # Mantener solo los datos dentro de la ventana de tiempo
    if len(xdata) > 0:
        current_time = xdata[-1]
        start_time = current_time - window_duration
        xdata = [x for x in xdata if x >= start_time]
        ydata = ydata[-len(xdata):]
    
    ax.set_xlim(xdata[0], xdata[-1])  # Ajustar el límite del eje x dinámicamente
    ln.set_data(xdata, ydata)

    return ln,

# Configura la animación
ani = FuncAnimation(fig, update, frames=range((len(df) // 2000)), init_func=init, blit=True, interval=100)

plt.show()
