import logging
import numpy as np
import pandas as pd
from src.config.config import PRECIO_MAXIMO, AREA_MAXIMA
logger = logging.getLogger('ProyectoAlquileres.Datos')


def load_data(filepath):
    try:
        df = pd.read_excel(filepath)
        logger.info('Datos cargados: %s; filas: %s',filepath,len(df))
        return df
    except Exception:
        logger.exception('No se pudo cargar el Excel: %s',filepath)
        raise


def clean_data(df):
    df = df.copy()
    columnas = ['precio_pen','area_m2','dormitorios','banos','distrito']
    for columna in columnas[:-1]:
        df[columna] = pd.to_numeric(df[columna],errors='coerce')
    df[columnas[:-1]] = df[columnas[:-1]].replace([np.inf,-np.inf],np.nan)
    df['distrito'] = df['distrito'].astype('string').str.strip().replace('',pd.NA)

    df['motivo_exclusion'] = ''
    df.loc[df[columnas].isna().any(axis=1),'motivo_exclusion'] = 'Dato esencial faltante'
    invalidos = (df['precio_pen']<=0)|(df['area_m2']<=0)|(df['dormitorios']<0)|(df['banos']<=0)
    df.loc[invalidos,'motivo_exclusion'] = 'Valor no válido'
    df.loc[df['precio_pen']>PRECIO_MAXIMO,'motivo_exclusion'] = 'Fuera del alcance: precio mayor al límite'
    df.loc[df['area_m2']>AREA_MAXIMA,'motivo_exclusion'] = 'Fuera del alcance: área superior a 400 m²'
    excluidos = df[df['motivo_exclusion']!=''].copy()
    df = df[df['motivo_exclusion']==''].drop(columns='motivo_exclusion')
    df = df.drop_duplicates('url')

    df = df.drop_duplicates(['titulo']+columnas).reset_index(drop=True)
    logger.info(f'\nAnuncios para el análisis: {len(df)}; excluidos por calidad o alcance: {len(excluidos)}.')
    logger.info('Variables: área, dormitorios, baños, estacionamientos y distrito. Objetivo: alquiler anunciado en soles.')
    logger.info('Prueba: los estacionamientos no indicados se rellenan con cero.')


    df['estacionamientos'] = pd.to_numeric(df['estacionamientos'],errors='coerce').fillna(0)

    return df, excluidos
