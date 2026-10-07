"""Pruebas de las reglas acordadas; ejecutar con unittest desde la raíz."""
import unittest
import pandas as pd
from src.data.make_dataset import clean_data

class TestCleanData(unittest.TestCase):
    def test_limite_de_area_y_precio(self):
        base = dict(precio_pen=20000,area_m2=400,dormitorios=2,banos=2,
                    estacionamientos=None,distrito='Miraflores')
        filas = [dict(base,url='a',titulo='a'),
                 dict(base,url='b',titulo='b',area_m2=401),
                 dict(base,url='c',titulo='c',precio_pen=20001)]
        limpio,excluidos = clean_data(pd.DataFrame(filas))
        self.assertEqual(limpio.url.tolist(),['a'])
        self.assertEqual(len(excluidos),2)
        self.assertEqual(limpio.estacionamientos.iloc[0],0)

    def test_no_inventar_precio_faltante(self):
        fila = dict(url='a',titulo='a',precio_pen=None,area_m2=80,
                    dormitorios=2,banos=2,estacionamientos=1,distrito='Miraflores')
        limpio,excluidos = clean_data(pd.DataFrame([fila]))
        self.assertTrue(limpio.empty)
        self.assertEqual(excluidos.motivo_exclusion.iloc[0],'Dato esencial faltante')

if __name__ == '__main__':
    unittest.main()
