import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0,str(BASE_DIR))
from src.config.config import PATHS, FEATURES, TARGET, USAR_EXCEL_EXISTENTE, CONSULTA_INTERACTIVA
from src.data.make_dataset import load_data, clean_data
from src.data.scrape_data import scraping
from src.features.build_features import split_features_target, build_features
from src.models.train_model import train_models, save_model, save_reports
from src.models.predict_model import consultar_departamento


def setup_logger():
    """FileHandler y StreamHandler como en clase; evitar duplicados en Spyder."""
    PATHS['LOGGING_FILE'].parent.mkdir(parents=True,exist_ok=True)
    logger = logging.getLogger('ProyectoAlquileres')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    formato = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    for handler in [logging.FileHandler(PATHS['LOGGING_FILE'],mode='a',encoding='utf-8'),logging.StreamHandler()]:
        handler.setFormatter(formato)
        logger.addHandler(handler)
    return logger


def run_pipeline(interactivo=CONSULTA_INTERACTIVA):
    logger = setup_logger()
    logger.info('INICIANDO FLUJO DE ALQUILERES')
    try:
        for ruta in PATHS.values():
            ruta.parent.mkdir(parents=True,exist_ok=True)
        # 1. Ingesta de datos guardados o scraping.
        if USAR_EXCEL_EXISTENTE and PATHS['RAW_DATA'].is_file():
            logger.info('Se encontró el Excel; se utilizarán los datos guardados.')
            df_raw = load_data(PATHS['RAW_DATA'])
        else:
            logger.info('Excel ausente o nueva descarga solicitada: iniciando scraping.')
            df_raw = scraping()
        # 2. Limpieza y trazabilidad.
        df,excluidos = clean_data(df_raw)
        df.to_excel(PATHS['PROCESSED_DATA'],index=False)
        excluidos.to_excel(PATHS['EXCLUDED_DATA'],index=False)
        if len(df)<100:
            raise ValueError('Se requieren al menos 100 anuncios válidos para esta comparación.')
        # 3. Variables y división entrenamiento/prueba.
        X,y = split_features_target(df,FEATURES,TARGET)
        X_train,X_test,y_train,y_test,X_train_scaled,X_test_scaled,scaler,distritos = build_features(X,y)
        # 4. Entrenamiento y evaluación.
        modelos,resultados,predicciones = train_models(df,X_train_scaled,X_test_scaled,y_train,y_test)
        # 5. Guardar modelos y reportes.
        bundle = {'modelos':modelos,'scaler':scaler,'columnas':X_train.columns.tolist(),'distritos':distritos}
        save_model(bundle,PATHS['MODEL_STORE'])
        save_reports(modelos,resultados,predicciones,y_train,y_test)
        # 6. Consulta opcional de departamentos nuevos.
        if interactivo:
            consultar_departamento(df.loc[y_train.index],modelos,scaler,X_train.columns)
        logger.info('FLUJO FINALIZADO CORRECTAMENTE')
        return df,resultados,modelos,scaler,predicciones
    except Exception:
        logger.exception('El flujo no pudo completarse.')
        raise


if __name__ == '__main__':
    df,resultados,modelos,scaler,predicciones = run_pipeline()
