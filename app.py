from flask import Flask, render_template
import pandas as pd
import os

from georef_func import georreferenciar_municipios
from pasos import pasos

SAMPLE_SIZE = 1000

df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'assets', 'data.csv')).sample(n=SAMPLE_SIZE, random_state=1).reset_index(drop=True)
samples = []

col_mapping = {
    "DIA_TRANSPORTE": "fecha",
    "NOMBRE_EMPRESA": "empresa",
    "LINEA": "linea",
    "AMBA": "amba",
    "TIPO_TRANSPORTE": "tipo_transporte",
    "JURISDICCION": "jurisdiccion",
    "PROVINCIA": "provincia",
    "MUNICIPIO": "municipio",
    "CANTIDAD": "cantidad",
    "DATO_PRELIMINAR": "dato_preliminar"
}


# Paso 0 - Datos originales
samples.append(df)

# Paso 1 - Datos normalizados
df_normalizado = df.rename(columns=col_mapping)
samples.append(df_normalizado)

# Paso 2 - Datos agregados
df_aggregated_prov_tipo = df_normalizado.groupby(['provincia', 'tipo_transporte']).size().reset_index(name='cantidad')
samples.append(df_aggregated_prov_tipo)

# Paso 3 - Gráfico de Barras - Viajes por tipo de transporte
samples.append(df_aggregated_prov_tipo.groupby('tipo_transporte')['cantidad'].sum().to_dict())

# Paso 4 - Gráfico de Barras - Viajes por tipo de transporte - limpio
## sin provincia "JN" ni LANCHAS y sin SN/SD en columna MUNICIPIO
# Elimino JN
df_limpio = df_normalizado[df_normalizado['provincia'] != 'JN']

# Elimino LANCHAS
df_limpio = df_limpio[df_limpio['tipo_transporte'] != 'LANCHAS']

# Elimino SN/SD en MUNICIPIO
df_limpio = df_limpio[~df_limpio['municipio'].isin(['SN', 'SD'])]

df_agg_tipo_sin_jn = df_limpio.groupby(['linea']).size().reset_index(name='cantidad')

samples.append(df_agg_tipo_sin_jn.groupby('linea')['cantidad'].sum().nlargest(5).to_dict())

# Paso 5 - Gráfico de Barras Horizontal - Top 5 provincias por cantidad de viajes
# Sumar por provincia
df_top5_provincias = df_limpio.groupby('provincia')['cantidad'].sum().nlargest(5)

# Convertir a diccionario para gráfico
data_top5 = df_top5_provincias.to_dict()
samples.append(data_top5)

# Paso 6 - Georreferenciacion
df_georreferenciada = georreferenciar_municipios(df_limpio.copy())
df_georreferenciada = df_georreferenciada.dropna(subset=['lat', 'lon'])
samples.append(df_georreferenciada)
samples.append(df_georreferenciada)



app = Flask(__name__)

@app.route('/')
def bienvenidos():
    return ''

@app.route('/paso/<int:n>')
def paso(n):
    if n < 4 or n==7:
        return render_template('tabla_datos.html', columnas=samples[n-1].columns.tolist(), datos=samples[n-1].values.tolist(), n=n)
    else:
        return pasos(samples[n-1], n)