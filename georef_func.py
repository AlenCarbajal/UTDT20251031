import pandas as pd
import requests
import folium


def georreferenciar_municipios(df):
    """
    Realiza una consulta POST a la API Georef V2 para el recurso 'gobiernos_locales'
    y devuelve df con latitud/longitud añadidas.
    """
    url = "https://apis.datos.gob.ar/georef/api/v2.0/gobiernos-locales"
    # Construir lista de objetos para la petición
    items = []
    for prov, mun in df[['provincia', 'municipio']].drop_duplicates().dropna().itertuples(index=False):
        obj = {"nombre": str(mun), "max": 1, "exacto": True}
        if pd.notna(prov):
            obj["provincia"] = str(prov)
        items.append(obj)


    body = {"gobiernos_locales": items}
    resp = requests.post(url, json=body)
    resp.raise_for_status()
    result = resp.json()

    referencias = []
    for i, res in enumerate(result.get("resultados", [])):
        locs = res.get("gobiernos_locales", [])
        if locs:
            loc = locs[0]
            referencias.append({
                'municipio': df.iloc[i]['municipio'],  # usamos el municipio original
                "lat": loc.get("centroide", {}).get("lat"),
                "lon": loc.get("centroide", {}).get("lon"),
                "id_gob_local": loc.get("id"),
                "provincia_georef": loc.get("provincia", {}).get("nombre")
            })
        else:
            referencias.append({
                'municipio': df.iloc[i]['municipio'],
                "lat": None,
                "lon": None,
                "id_gob_local": None,
                "provincia_georef": None
            })

    df_ref = pd.DataFrame(referencias)
    df_final = df.merge(df_ref, on='municipio', how='left')

    return df_final

import folium
import json
from folium.plugins import HeatMap

import folium
import json
import os
import numpy as np

def mapa_municipios(df, geojson_path="assets/municipios.geojson"):
    """
    Devuelve un mapa OSM con polígonos de municipios coloreados según cantidad.
    df debe tener columnas: 'id_gob_local', 'cantidad', 'municipio'
    geojson_path: ruta al GeoJSON de municipios
    """

    # Cargar GeoJSON
    with open(os.path.join(os.path.dirname(__file__), geojson_path), "r", encoding="utf-8") as f:
        geojson_muns = json.load(f)

    # Filtrar solo municipios con datos
    id_to_cant = df.set_index('id_gob_local')['cantidad'].to_dict()
    features_filtradas = []
    for feature in geojson_muns['features']:
        id_mun = feature['properties']['id']
        cant = id_to_cant.get(id_mun, 0)
        if cant > 0:
            feature['properties']['cantidad'] = cant
            features_filtradas.append(feature)
    geojson_muns['features'] = features_filtradas

    # Crear mapa minimalista
    mapa = folium.Map(location=[-38, -63], zoom_start=4, tiles="CartoDB positron")

    # Escala de colores proporcional
    cantidades = np.array([f['properties']['cantidad'] for f in features_filtradas])
    min_c, max_c = cantidades.min(), cantidades.max()
    def estilo(feature):
        cant = feature['properties']['cantidad']
        # Normalizar entre 0 y 1
        norm = (cant - min_c) / (max_c - min_c + 1e-5)
        # Gradiente rojo (claro → oscuro)
        r = int(50 + 205*norm)
        color = f"#{r:02x}0000"
        return {"fillColor": color, "color": "black", "weight": 1, "fillOpacity": 0.7}

    folium.GeoJson(
        geojson_muns,
        style_function=estilo,
        tooltip=folium.GeoJsonTooltip(fields=['nombre', 'cantidad'])
    ).add_to(mapa)

    return mapa

