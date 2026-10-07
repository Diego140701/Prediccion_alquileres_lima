"""Acceso sencillo desde Spyder o VS Code."""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0,str(BASE_DIR))
from src.main_pipeline import run_pipeline

if __name__ == '__main__':
    df,resultados,modelos,scaler,predicciones = run_pipeline()
