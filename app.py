from flask import Flask, request, render_template, send_file
import pandas as pd
import numpy as np
from io import BytesIO
import os
import matplotlib.pyplot as plt
import seaborn as sns


# Crea una instancia de la aplicación Flask
app = Flask(__name__)

# Asegúrate de que el directorio 'uploads' exista
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Variable global para almacenar el DataFrame
df = None

# Define una ruta para la página principal ('/')
@app.route('/', methods=['GET', 'POST'])
def index():
    global df  # Permite modificar la variable global 'df'
    
    # Si la solicitud es de tipo POST (es decir, se ha enviado un formulario)
    if request.method == 'POST':
        file = request.files['file']  # Obtén el archivo enviado con el formulario
        
        # Verifica que el archivo existe y tiene una extensión .csv
        if file and file.filename.endswith('.csv'):
            file_path = os.path.join('uploads', file.filename)  # Construye la ruta del archivo
            file.save(file_path)  # Guarda el archivo en el directorio 'uploads'
            df = pd.read_csv(file_path)  # Lee el archivo CSV en un DataFrame de pandas
            
            cat_vars = df.select_dtypes(include=['object']).columns
            num_vars = df.select_dtypes(include=['int64', 'float64']).columns
            
            # Resumen de variables categóricas
            cat_summary = df[cat_vars].describe().to_html()
            
            # Resumen de variables numéricas
            num_summary = df[num_vars].describe().to_html()
            
            # Información sobre valores nulos
            null_counts = df.isnull().sum()
            null_percentages = 100 * df.isnull().sum() / len(df)
            null_table = pd.concat([null_counts, null_percentages], axis=1, 
                                   keys=['Conteo de Nulos', 'Porcentaje de Nulos'])
            null_table = null_table[null_table['Conteo de Nulos'] > 0].sort_values('Conteo de Nulos', ascending=False)
            null_summary = null_table.to_html()
            
            # Renderiza la plantilla 'result.html' con los datos del DataFrame
            return render_template('result.html', 
                                   data=df.head().to_html(),  # Convierte los primeros 5 registros del DataFrame a HTML
                                   stats=df.describe().to_html(),
                                   cat_summary=cat_summary,
                                   num_summary=num_summary,
                                   null_summary=null_summary)  # Convierte las estadísticas del DataFrame a HTML
    
    # Si la solicitud es de tipo GET, simplemente renderiza la plantilla 'index.html'
    return render_template('index.html')


# Ruta para mostrar un gráfico
@app.route('/plot')
def plot():
    
    global df
    if df is not None:  # Verifica que el DataFrame no esté vacío
        fig, ax = plt.subplots()  # Crea una figura y un eje para el gráfico
        sns.histplot(df.iloc[:, 0], kde=True, ax=ax)  # Crea un histograma de la primera columna del DataFrame
        output = BytesIO()  # Crea un buffer en memoria para guardar el gráfico
        fig.savefig(output, format='png')  # Guarda el gráfico en el buffer
        output.seek(0)  # Mueve el cursor al inicio del buffer
        return send_file(output, mimetype='image/png')  # Envía el gráfico como una imagen PNG
    return "No hay datos para graficar", 404  # Mensaje de error si no hay datos



        
@app.route('/download')
def download_csv():
    global df  # Accede a la variable global 'df'
    
    # Verifica que 'df' no sea None
    if df is not None:
        output = BytesIO()  # Crea un objeto BytesIO en memoria
        df.to_csv(output, index=False)  # Escribe el DataFrame 'df' en el objeto BytesIO como un archivo CSV, sin el índice
        output.seek(0)  # Mueve el puntero al inicio del objeto BytesIO para que la lectura comience desde el principio
        
        # Envía el archivo CSV como respuesta al cliente
        return send_file(output, 
                         mimetype='text/csv',  # Establece el tipo MIME del archivo como 'text/csv'
                         as_attachment=True,  # Indica que el archivo debe ser descargado como un adjunto
                         download_name='processed_data.csv')  # Establece el nombre del archivo de descarga
    
    # Si 'df' es None, devuelve un mensaje de error con el código de estado 404
    return "No hay datos para descargar", 404

if __name__ == '__main__':
    app.run(debug=True)