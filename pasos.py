import io
import base64
from flask import render_template
import matplotlib.pyplot as plt
from .georef_func import mapa_municipios

def pasos(data, n):
    if n == 4:
        return render_template('grafico.html', title="Viajes por tipo de transporte", image=grafico_barras_vertical(data), n=n)
    elif n == 5:
        return render_template('grafico.html', title="Viajes por tipo de transporte - Colectivos", image=grafico_barras_vertical(data), n=n)
    elif n == 6:
        return render_template('grafico.html', title="Top 5 Provincias por Cantidad de Viajes", image=grafico_barras_horizontal(data), n=n)
    elif n == 8:
        mapa = mapa_municipios(data)
        mapa_html = mapa._repr_html_()  # genera el HTML como string
        return render_template("mapa_template.html", mapa_html=mapa_html, n=n)

        
def grafico_barras_vertical(data):
    # Crear gráfico de barras
    fig, ax = plt.subplots(figsize=(7,5))
    barras = ax.bar(data.keys(), data.values(), color="#1f77b4", edgecolor="#0b3d91", linewidth=1.5)

    # Estética
    ax.set_facecolor("#f9f9f9")             # fondo del gráfico
    fig.patch.set_facecolor("#f9f9f9")      # fondo figura
    ax.set_ylabel("Cantidad", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Añadir etiquetas sobre las barras
    for barra in barras:
        height = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2, height + 0.5, f'{height}', ha='center', va='bottom', fontsize=11)

    # Convertir a imagen base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode()
    buf.close()

    return image_base64

def grafico_barras_horizontal(data):
    # data es un diccionario: {provincia: cantidad}

    provincias = list(data.keys())
    cantidades = list(data.values())
    
    # Gráfico horizontal
    fig, ax = plt.subplots(figsize=(7,5))
    barras = ax.barh(provincias[::-1], cantidades[::-1], color="#1f77b4", edgecolor="#0b3d91", linewidth=1.5)

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Etiquetas
    for barra in barras:
        width = barra.get_width()
        ax.text(width + 0.2, barra.get_y() + barra.get_height()/2, f'{int(width)}', va='center', fontsize=11)

    # Convertir a imagen base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode()
    buf.close()
    return image_base64

