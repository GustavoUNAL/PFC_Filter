import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Ruta del archivo CSV
csv_file = 'test.csv'

# Configuración inicial de la figura y el gráfico
fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'r-', animated=True)

# Lee el CSV para obtener el rango total de tiempo
df = pd.read_csv(csv_file)
time_max = df['Time'].max()

# Función de inicialización
def init():
    ax.set_xlim(0, time_max)  # Ajusta el límite del eje x basado en el rango total de tiempo
    ax.set_ylim(df['Sine Wave3'].min(), df['Sine Wave3'].max())  # Ajusta el límite del eje y basado en los datos
    return ln,

# Función de actualización
def update(frame):
    # Leer sólo una porción de datos
    chunk_size = 2000  # Número de filas por chunk
    skiprows = frame * chunk_size + 1  # Saltar la primera fila con nombres de columna y los chunks anteriores
    df_chunk = pd.read_csv(csv_file, skiprows=skiprows, nrows=chunk_size, names=['Time', 'Sine Wave3'], header=None)
    
    df_chunk['Time'] = pd.to_numeric(df_chunk['Time'], errors='coerce')
    df_chunk['Sine Wave3'] = pd.to_numeric(df_chunk['Sine Wave3'], errors='coerce')

    xdata.extend(df_chunk['Time'].dropna())
    ydata.extend(df_chunk['Sine Wave3'].dropna())
    ln.set_data(xdata, ydata)

    return ln,

# Configura la animación
ani = FuncAnimation(fig, update, frames=range((len(df) // 2000)), init_func=init, blit=True, interval=100)

plt.show()
