import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.config.config import TEST_SIZE, RANDOM_STATE
logger = logging.getLogger('ProyectoAlquileres.Variables')


def split_features_target(df, feature_cols, target_col):
    logger.info('Separando variables X y objetivo y.')
    return df[feature_cols], df[target_col]


def build_features(X,y):
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=TEST_SIZE,random_state=RANDOM_STATE)
    distritos = sorted(X_train['distrito'].unique())
    X_train = pd.get_dummies(X_train,columns=['distrito'],drop_first=True,dtype=int)
    X_test = pd.get_dummies(X_test,columns=['distrito'],dtype=int)
    X_test = X_test.reindex(columns=X_train.columns,fill_value=0)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    logger.info('Entrenamiento: %s; prueba: %s.',len(y_train),len(y_test))
    return X_train,X_test,y_train,y_test,X_train_scaled,X_test_scaled,scaler,distritos
