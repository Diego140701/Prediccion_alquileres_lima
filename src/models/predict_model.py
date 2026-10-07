import logging
import pickle
import pandas as pd
import numpy as np
from src.config.config import AREA_MAXIMA
logger = logging.getLogger('ProyectoAlquileres.Prediccion')


def load_model(filepath):
    with open(filepath,'rb') as archivo:
        bundle = pickle.load(archivo)
    logger.info('Modelos recuperados: %s',filepath)
    return bundle

def predecir_departamento(area, dormitorios, banos, estacionamientos, distrito,
                         modelos, scaler, columnas):
    # Crear una fila con las mismas variables del entrenamiento.
    nuevo = pd.DataFrame([{
        'area_m2':area, 'dormitorios':dormitorios, 'banos':banos,
        'estacionamientos':estacionamientos, 'distrito':distrito
    }])
    nuevo = pd.get_dummies(nuevo,columns=['distrito'],dtype=int)
    # Mismas columnas y mismo orden; el distrito de referencia queda con ceros.
    nuevo = nuevo.reindex(columns=columnas,fill_value=0)
    nuevo_scaled = scaler.transform(nuevo)  # No volver a ajustar el scaler.
    estimaciones = []
    for nombre,modelo in modelos.items():
        precio = modelo.predict(nuevo_scaled)[0]
        estimaciones.append({'Modelo':nombre,'Alquiler estimado (S/mes)':round(precio,2)})
    logger.info('Predicción realizada para un departamento de %s m² en %s.',area,distrito)
    return pd.DataFrame(estimaciones)

def pedir_numero(mensaje, minimo, maximo, entero=False):
    while True:
        try:
            valor = float(input(mensaje).strip().replace(',','.'))
            if not np.isfinite(valor) or not minimo <= valor <= maximo:
                raise ValueError
            if entero and not valor.is_integer():
                raise ValueError
            return int(valor) if entero else valor
        except ValueError:
            print(f'Ingresa un número {"entero " if entero else ""}entre {minimo} y {maximo}.')

def consultar_departamento(df_train, modelos, scaler, columnas):
    while input('\n¿Deseas estimar un departamento nuevo? (s/n): ').strip().lower() in ['s','si','sí']:
        area = pedir_numero('Área en m²: ',1,AREA_MAXIMA)
        dormitorios = pedir_numero('Número de dormitorios: ',0,20,entero=True)
        banos = pedir_numero('Número de baños: ',1,20,entero=True)
        estacionamientos = pedir_numero('Número de estacionamientos: ',0,20,entero=True)
        distritos = sorted(df_train['distrito'].unique())
        print('\nDistritos disponibles en entrenamiento:')
        for i,distrito in enumerate(distritos,1):
            print(f'{i}. {distrito}')
        opcion = pedir_numero('Elige el número del distrito: ',1,len(distritos),entero=True)
        distrito = distritos[opcion-1]
        estimaciones = predecir_departamento(area,dormitorios,banos,estacionamientos,
                                            distrito,modelos,scaler,columnas)
        print(f'\nEstimaciones para {distrito}:')
        print(estimaciones.to_string(index=False))
        print('Alquiler mensual anunciado.')
