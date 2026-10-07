from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PATHS = {
    'RAW_DATA': BASE_DIR/'data'/'raw'/'anuncios.xlsx',
    'PROCESSED_DATA': BASE_DIR/'data'/'processed'/'anuncios_limpios.xlsx',
    'EXCLUDED_DATA': BASE_DIR/'data'/'processed'/'registros_excluidos.xlsx',
    'PREDICTIONS': BASE_DIR/'data'/'processed'/'predicciones.xlsx',
    'MODEL_STORE': BASE_DIR/'models'/'modelos.pkl',
    'LOGGING_FILE': BASE_DIR/'logs'/'pipeline.log',
    'METRICS': BASE_DIR/'reports'/'comparacion_modelos.xlsx',
    'FIGURE': BASE_DIR/'reports'/'real_vs_estimado.png',
}
USAR_EXCEL_EXISTENTE = True
CONSULTA_INTERACTIVA = True
NUMERO_DISTRITOS = 17
PRECIO_MAXIMO = 20000
AREA_MAXIMA = 400
NUMERIC_FEATURES = ['area_m2','dormitorios','banos','estacionamientos']
CATEGORICAL_FEATURES = ['distrito']
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = 'precio_pen'
TEST_SIZE = 0.2
RANDOM_STATE = 42
DISTRITOS = ['miraflores','san-isidro','santiago-de-surco','san-miguel',
             'barranco','jesus-maria','lince','surquillo','magdalena',
             'pueblo-libre','san-borja','lima-cercado','la-molina',
             'chorrillos','la-victoria','los-olivos','brena']
