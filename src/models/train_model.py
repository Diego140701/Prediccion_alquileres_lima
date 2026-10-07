import logging
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.config.config import PATHS
logger = logging.getLogger('ProyectoAlquileres.Modelos')


def train_models(df,X_train_scaled,X_test_scaled,y_train,y_test):
    modelos = {
        'Regresion Lineal':LinearRegression(),
        'Ridge':Ridge(alpha=1.0),
        'Lasso':Lasso(alpha=0.1,max_iter=10000),
        'Random Forest':RandomForestRegressor(n_estimators=100,min_samples_leaf=3,random_state=42),
        'Gradient Boosting':GradientBoostingRegressor(n_estimators=100,random_state=42)
    }
    resultados = []
    predicciones = df.loc[y_test.index,['url','distrito']].copy()
    predicciones['precio_real_pen'] = y_test
    for nombre,modelo in modelos.items():
        modelo.fit(X_train_scaled,y_train)
        pred = modelo.predict(X_test_scaled)
        mse = mean_squared_error(y_test,pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test,pred)
        r2 = r2_score(y_test,pred)
        logger.info(f'\n{nombre}: MSE={mse:.2f} | RMSE={rmse:.2f} | MAE=S/ {mae:.2f} | R2={r2:.4f}')
        resultados.append({'Modelo':nombre,'MSE':mse,'RMSE':rmse,'MAE':mae,'R2':r2})
        predicciones[nombre] = pred

    return modelos,pd.DataFrame(resultados).sort_values("MAE"),predicciones


def save_model(bundle,filepath):
    filepath.parent.mkdir(parents=True,exist_ok=True)
    with open(filepath,'wb') as archivo:
        pickle.dump(bundle,archivo)
    logger.info('Modelos y transformaciones guardados: %s',filepath)


def save_reports(modelos,resultados,predicciones,y_train,y_test):
    referencia = np.full(len(y_test),y_train.median())
    mae_referencia = mean_absolute_error(y_test,referencia)
    logger.info(f'\nMAE de referencia (mediana de entrenamiento): S/ {mae_referencia:.2f}')
    logger.info('\nComparación de modelos (menor MAE primero):')
    logger.info(resultados.to_string(index=False))
    resultados.to_excel(PATHS['METRICS'],index=False)
    predicciones.to_excel(PATHS['PREDICTIONS'],index=False)
    fig,axes = plt.subplots(2,3,figsize=(12,8))
    for ax,nombre in zip(axes.flat,modelos):
        ax.scatter(y_test,predicciones[nombre],alpha=0.5,s=15)
        limites = [min(y_test.min(),predicciones[nombre].min()),max(y_test.max(),predicciones[nombre].max())]
        ax.plot(limites,limites,'r--')
        ax.set(title=nombre,xlabel='Precio real (S/)',ylabel='Precio estimado (S/)')
    axes.flat[-1].axis('off')
    fig.tight_layout()
    fig.savefig(PATHS['FIGURE'],dpi=150)
    plt.close(fig)
    logger.info('Reportes guardados en: %s',PATHS['METRICS'].parent)
