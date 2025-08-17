
#importaciones de librerias
import numpy as np
import random
from datetime import datetime
from fastapi import FastAPI
from threading import Thread
import time
from collections import deque
import json
import os

#configuracion de la api
app = FastAPI(title="Invernadero")

# creacion de los archivos de persistencia para guardar los datos
PH_datos = "ph.json"
humedad_datos = "humedad.json"
temperatura_datos = "temperatura.json"

#funciones de cargar y guardar
def cargar(nombre, maxlen):
    if os.path.exists(nombre):
        with open(nombre, "r") as f:
            return deque(json.load(f), maxlen=maxlen)
    return deque(maxlen=maxlen)

def guardar(nombre, historial):
    with open(nombre, "w") as f:
        json.dump(list(historial), f, indent=4)

# Historiales con persistencia
registro_ph = cargar(PH_datos, maxlen=12)
registro_humedad = cargar(humedad_datos, maxlen=12)
registro_temp = cargar(temperatura_datos, maxlen=200)

# Simulación de sensores
def generar_ph():
    while True:
        valor = round(random.uniform(5.5, 7.5), 2)
        registro_ph.append({"timestamp": datetime.now().isoformat(), "valor": valor})
        guardar(PH_datos, registro_ph)
        time.sleep(6 * 60 * 60)  # 6 horas

def generar_humedad():
    while True:
        valor = round(random.uniform(60, 90), 2)
        registro_humedad.append({"timestamp": datetime.now().isoformat(), "valor": valor})
        guardar(humedad_datos, registro_humedad)
        time.sleep(2 * 60 * 60)  # 2 horas

def generar_temperatura():
    while True:
        hora_actual = datetime.now().hour + datetime.now().minute / 60
        valor = 20 + 5 * np.sin(2 * np.pi * hora_actual / 24) + random.uniform(-0.3, 0.3)
        valor = round(valor, 2)
        registro_humedad.append({"timestamp": datetime.now().isoformat(), "valor": valor})
        guardar(temperatura_datos, registro_temp)
        time.sleep(5)  # 5 segundos

# Endpoints
@app.get("/temperatura")
def get_temperatura():
    return {
        "ultima": registro_temp[-1] if registro_temp else None,
        "ultimas_10": list(registro_temp)[-10:]
    }

@app.get("/humedad")
def get_humedad():
    return {
        "ultima": registro_humedad[-1] if registro_humedad else None,
        "historial": list(registro_humedad)
    }

@app.get("/ph")
def get_ph():
    return {
        "historial": list(registro_ph)
    }

# Inicio del servidor con threads
if __name__ == "__main__":
    Thread(target=generar_ph, daemon=True).start()
    Thread(target=generar_humedad, daemon=True).start()
    Thread(target=generar_temperatura, daemon=True).start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)