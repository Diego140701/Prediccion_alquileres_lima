import logging
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from src.config.config import BASE_DIR, PATHS, NUMERO_DISTRITOS, DISTRITOS
logger = logging.getLogger('ProyectoAlquileres.Scraping')

def obtener_numero(patron, texto):
    coincidencia = re.search(patron,texto,re.IGNORECASE)
    if coincidencia is None:
        return None
    valor = coincidencia.group(1).replace(' ','')
    if ',' in valor and '.' in valor:
        if valor.rfind(',') > valor.rfind('.'):
            valor = valor.replace('.','').replace(',','.')
        else:
            valor = valor.replace(',','')
    elif ',' in valor or '.' in valor:
        separador = ',' if ',' in valor else '.'
        if len(valor.split(separador)[-1]) == 3:
            valor = valor.replace(separador,'')
        else:
            valor = valor.replace(separador,'.')
    return float(valor)

def leer_tarjeta(html, enlace):
    tarjeta = BeautifulSoup(html,'html.parser')
    def texto(campo):
        elemento = tarjeta.select_one(f'[data-qa="{campo}"]')
        return elemento.get_text(' ',strip=True) if elemento else ''
    precio = texto('POSTING_CARD_PRICE')
    caracteristicas = texto('POSTING_CARD_FEATURES')
    ubicacion = texto('POSTING_CARD_LOCATION')
    partes = [parte.strip() for parte in ubicacion.split(',') if parte.strip()]
    if partes and partes[-1].lower() == 'lima':
        partes.pop()
    distrito = partes[-1] if partes else None
    imagen = tarjeta.select_one('img[alt]')
    return {
        'url':enlace, 'titulo':imagen.get('alt','') if imagen else '',
        'precio_pen':obtener_numero(r'S/\.?\s*([\d][\d., ]*)',precio),
        'area_m2':obtener_numero(r'([\d.,]+)\s*m[²2]',caracteristicas),
        'dormitorios':obtener_numero(r'(\d+)\s*dorm',caracteristicas),
        'banos':obtener_numero(r'(\d+(?:[.,]\d+)?)\s*baño',caracteristicas),
        'estacionamientos':obtener_numero(r'(\d+)\s*estac',caracteristicas),
        'distrito':distrito,
        'precio_original':precio, 'caracteristicas_originales':caracteristicas,
        'fecha_extraccion':datetime.now().isoformat(timespec='seconds')
    }

def scraping():
    if not 1 <= NUMERO_DISTRITOS <= len(DISTRITOS):
        raise ValueError('NUMERO_DISTRITOS debe estar entre 1 y 17.')
    salida = PATHS['RAW_DATA'].parent
    salida.mkdir(parents=True,exist_ok=True)
    os.environ['SE_CACHE_PATH'] = str(BASE_DIR/'.selenium')
    opciones = Options()
    opciones.add_argument('--start-maximized')
    opciones.add_argument('--disable-notifications')
    datos = []
    completados = 0
    selector = '[data-posting-type="PROPERTY"][data-to-posting*="/inmueble/clasificado/"]'
    for distrito in DISTRITOS[:NUMERO_DISTRITOS]:
        url = f'https://urbania.pe/buscar/alquiler-de-departamentos-en-{distrito}--lima--lima'
        logger.info(f'Abriendo una sesión nueva para {distrito}...')
        driver = webdriver.Edge(options=opciones)
        driver.set_page_load_timeout(60)
        espera = WebDriverWait(driver,30)
        try:
            driver.get(url)
            cuerpo = driver.find_element(By.TAG_NAME,'body').text.lower()
            if any(t in cuerpo for t in ['access denied','verify you are human','just a moment']):
                raise RuntimeError('La página pide una verificación de acceso.')
            tarjetas = espera.until(lambda d: d.find_elements(By.CSS_SELECTOR,selector))
            for tarjeta in tarjetas:
                enlace = urljoin(driver.current_url,tarjeta.get_attribute('data-to-posting')).split('?')[0]
                fila = leer_tarjeta(tarjeta.get_attribute('outerHTML'),enlace)
                fila['distrito_consultado'] = distrito
                datos.append(fila)
            pd.DataFrame(datos).drop_duplicates('url').to_excel(salida/'anuncios.xlsx',index=False)
            completados += 1
            logger.info(f'  {len(tarjetas)} tarjetas leídas.')
            time.sleep(2)
        except (TimeoutException,RuntimeError) as error:
            logger.warning('No se completó %s: %s',distrito,type(error).__name__)
            if isinstance(error,RuntimeError):
                break
        finally:
            driver.quit()
            logger.info(f'  Sesión de {distrito} cerrada.')
    if not datos:
        raise RuntimeError(f'No se extrajeron anuncios. Revisa el registro de logging.')

    df = pd.DataFrame(datos).drop_duplicates('url')
    df.to_excel(salida/'anuncios.xlsx',index=False)
    esenciales = ['precio_pen','area_m2','dormitorios','banos','distrito']
    completos = df.dropna(subset=esenciales)
    logger.info(df[esenciales].head().to_string(index=False))
    logger.info(f'Anuncios únicos: {len(df)}; con datos esenciales completos: {len(completos)}.')
    logger.info(f'Distritos completados: {completados}/{NUMERO_DISTRITOS}.')
    logger.info(f'Excel: {salida / "anuncios.xlsx"}')
    logger.info('Esta es una muestra de primeras páginas por distrito, no todos los anuncios de Lima.')
    logger.info('Base RAW actualizada: %s',PATHS['RAW_DATA'])
    return df
