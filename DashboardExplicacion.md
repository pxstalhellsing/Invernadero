1) Encabezados / Imports

import streamlit as st
import pandas as pd
import requests

2) Config y título

API_URL = "http://127.0.0.1:8000"  

st.set_page_config(page_title="Invernadero Inteligente", layout="wide")
st.title("Datos graficos del invernadero")

API_URL apunta a la API local (debe estar corriendo, p. ej. uvicorn invernadero2:app).

set_page_config(..., layout="wide") hace que la UI use todo el ancho disponible.

st.title pone el título de la página.

4) Auto-refresh opcional

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=5000, key="auto_refresh")
except Exception:
    st.info("Auto-refresh opcional: instala 'streamlit-autorefresh' con:\n\npip install streamlit-autorefresh")

Intenta importar streamlit_autorefresh y si está, vuelve a ejecutar la app cada 5000 ms (5 s).

Si no está instalado muestra un mensaje con instrucciones.

5) Función

def obtener_datos(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}", timeout=2)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

Hace GET a http://127.0.0.1:8000/<endpoint> con timeout=2 segundos.

r.raise_for_status() fuerza excepción si el status != 2xx.

En cualquier excepción devuelve None.

6) Layout principal: 3 columnas y cada bloque

col1, col2, col3 = st.columns(3)

with col1:
    temp_data = obtener_datos("temperatura")
    if temp_data and temp_data.get("ultima"):
        ultima = temp_data["ultima"]
        st.metric("Temperatura actual (°C)", ultima.get("valor", "N/A"))
        df_temp = pd.DataFrame(temp_data.get("ultimas_10", []))
        if not df_temp.empty:
            df_temp["timestamp"] = pd.to_datetime(df_temp["timestamp"])
            df_temp = df_temp.set_index("timestamp").sort_index()
            st.line_chart(df_temp["valor"])
    else:
        st.warning("Temperatura: datos no disponibles (asegúrate de que la API esté corriendo)")

temp_data espera una estructura { "ultima": {...}, "ultimas_10": [ {...}, ... ] }.

st.metric muestra la última temperatura (valor simple).

Convierte ultimas_10 a DataFrame; convierte timestamp a datetime, lo pone como índice y ordena por fecha; finalmente traza la serie valor con st.line_chart()

hum_data = obtener_datos("humedad")
if hum_data and hum_data.get("ultima"):
    st.metric("Humedad actual (%)", hum_data["ultima"].get("valor", "N/A"))
    df_hum = pd.DataFrame(hum_data.get("historial", []))
    ...
else:
    st.warning("Humedad: datos no disponibles")

ph_data = obtener_datos("ph")
if ph_data and ph_data.get("historial"):
    df_ph = pd.DataFrame(ph_data["historial"])
    ...
    st.metric("Último pH", df_ph["valor"].iloc[-1])
    st.line_chart(df_ph["valor"])
else:
    st.warning("pH: datos no disponibles")

7) Debug
   with st.expander("Mostrar respuestas crudas (debug)"):
    st.write({
        "temperatura": temp_data,
        "humedad": hum_data,
        "ph": ph_data
    })
Muestra los JSON crudos obtenidos (útil para depurar formato de respuesta de la API).
