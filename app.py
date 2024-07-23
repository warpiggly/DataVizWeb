from flask import Flask, request, render_template, send_file
import pandas as pd
import numpy as np
from io import BytesIO
import os

app = Flask(__name__)

# Asegúrate de que el directorio 'uploads' exista
if not os.path.exists('uploads'):
    os.makedirs('uploads')

df = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            df = pd.read_csv(file_path)
            return render_template('result.html', 
                                   data=df.head().to_html(), 
                                   stats=df.describe().to_html())
    return render_template('index.html')

@app.route('/download')
def download_csv():
    global df
    if df is not None:
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, 
                         mimetype='text/csv', 
                         as_attachment=True, 
                         download_name='processed_data.csv')
    return "No hay datos para descargar", 404

if __name__ == '__main__':
    app.run(debug=True)