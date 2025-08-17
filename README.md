# Invernadero
Trabajo de invernadero con un dashboard
1) Encabezados / imports
import numpy as np
import random
from datetime import datetime
from fastapi import FastAPI
from threading import Thread
import time
from collections import deque
import json
import os

2) Configuración de la app y nombres de archivos

app = FastAPI(title="Invernadero")

PH_datos = "ph.json"
humedad_datos = "humedad.json"
temperatura_datos = "temperatura.json"

3) Persistencia: cargar y guardar

def cargar(nombre, maxlen):
    if os.path.exists(nombre):
        with open(nombre, "r") as f:
            return deque(json.load(f), maxlen=maxlen)
    return deque(maxlen=maxlen)

def guardar(nombre, historial):
    with open(nombre, "w") as f:
        json.dump(list(historial), f, indent=4)

4) Historiales iniciales

registro_ph = cargar(PH_datos, maxlen=12)
registro_humedad = cargar(humedad_datos, maxlen=12)
registro_temp = cargar(temperatura_datos, maxlen=200)


5) Simulación de sensores — explicación detallada

def generar_ph():
    while True:
        valor = round(random.uniform(5.5, 7.5), 2)
        registro_ph.append({"timestamp": datetime.now().isoformat(), "valor": valor})
        guardar(PH_datos, registro_ph)
        time.sleep(6 * 60 * 60)  # 6 horas

Genera aleatoriamente un pH entre 5.5 y 7.5, redondeado a 2 decimales.
Se actualiza cada 6 horas.


def generar_humedad():
    while True:
        valor = round(random.uniform(60, 90), 2)
        registro_humedad.append({"timestamp": datetime.now().isoformat(), "valor": valor})
        guardar(humedad_datos, registro_humedad)
        time.sleep(2 * 60 * 60)  # 2 horas

Simula humedad relativa entre 60% y 90%.

Intervalo: cada 2 horas; con maxlen=12 cubres 24 horas.


def generar_temperatura():
    while True:
        hora_actual = datetime.now().hour + datetime.now().minute / 60
        valor = 20 + 5 * np.sin(2 * np.pi * hora_actual / 24) + random.uniform(-0.3, 0.3)
        valor = round(valor, 2)
        registro_humedad.append({"timestamp": datetime.now().isoformat(), "valor": valor})
        guardar(temperatura_datos, registro_temp)
        time.sleep(5)  # 5 segundos

Intervalo: cada 5 segundos
modelar ciclo diario de temperatura con una formula 

6) Endpoints

@app.get("/temperatura")
def get_temperatura():
    return {
        "ultima": registro_temp[-1] if registro_temp else None,
        "ultimas_10": list(registro_temp)[-10:]
    }
Devuelve la última temperatura (o None si no hay datos) y las últimas 10.

registro_temp[-1] puede lanzar IndexError si registro_temp está vacío, por eso usan la comprobación if registro_temp else None.

@app.get("/humedad")
def get_humedad():
    return {
        "ultima": registro_humedad[-1] if registro_humedad else None,
        "historial": list(registro_humedad)
    }

Devuelve la última humedad y todo el historial en memoria (hasta maxlen)

@app.get("/ph")
def get_ph():
    return {
        "historial": list(registro_ph)
    }

Devuelve solo el historial del pH.

7) Inicio del proceso / threads y uvicorn

   if __name__ == "__main__":
    Thread(target=generar_ph, daemon=True).start()
    Thread(target=generar_humedad, daemon=True).start()
    Thread(target=generar_temperatura, daemon=True).start()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


