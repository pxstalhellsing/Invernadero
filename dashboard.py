#---NOTA IMPORTANTE---
#primero se ejecuta el invernadero y luego se abre otro terminal con python -m streamlit run dashboard.py
# dashboard.py
import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000"  



st.set_page_config(page_title="Invernadero Inteligente", layout="wide")
st.title("Datos graficos del invernadero")


try:
    from streamlit_autorefresh import st_autorefresh
    # refresca cada 5000 ms (5 segundos)
    st_autorefresh(interval=5000, key="auto_refresh")
except Exception:
    st.info("Auto-refresh opcional: instala 'streamlit-autorefresh' con:\n\npip install streamlit-autorefresh")

#obtener datos 
def obtener_datos(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}", timeout=2)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


#Visualizacion del los datos
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

with col2:
    hum_data = obtener_datos("humedad")
    if hum_data and hum_data.get("ultima"):
        st.metric("Humedad actual (%)", hum_data["ultima"].get("valor", "N/A"))
        df_hum = pd.DataFrame(hum_data.get("historial", []))
        if not df_hum.empty:
            df_hum["timestamp"] = pd.to_datetime(df_hum["timestamp"])
            df_hum = df_hum.set_index("timestamp").sort_index()
            st.line_chart(df_hum["valor"])
    else:
        st.warning("Humedad: datos no disponibles")

with col3:
    ph_data = obtener_datos("ph")
    if ph_data and ph_data.get("historial"):
        df_ph = pd.DataFrame(ph_data["historial"])
        if not df_ph.empty:
            df_ph["timestamp"] = pd.to_datetime(df_ph["timestamp"])
            df_ph = df_ph.set_index("timestamp").sort_index()
            st.metric("Último pH", df_ph["valor"].iloc[-1])
            st.line_chart(df_ph["valor"])
    else:
        st.warning("pH: datos no disponibles")


with st.expander("Mostrar respuestas crudas (debug)"):
    st.write({
        "temperatura": temp_data,
        "humedad": hum_data,
        "ph": ph_data
    })