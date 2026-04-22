# -*- coding: UTF-8 -*-
import sys
import os
from collections import deque
import pyproj
import shapely
from osgeo import gdal
from app.geo_controller import GeoController
from app.logger import Logger

# Configuração GDAL
os.environ['PROJ_LIB'] = pyproj.datadir.get_data_dir()

print('\nVerificando Bibliotecas:')
print(f'    Gdal: ------ {gdal.__version__}')
print(f'    Pyproj: ---- {pyproj.__version__}')
print(f'    Shapely: --- {shapely.__version__}')
print(' Bibliotecas importadas com sucesso!\n')

logs_dq = deque(maxlen=100)
logger = Logger(log_queue=logs_dq)
controller = GeoController(app_logger=logger)

# Arquivos shapefiles
# nome dos arquivos na pasta /files/shapefiles
shapes = ['camada-1.shp', 'camada-2.shp', 'camada-3.shp']

try:
    geojson_data = controller.intersect_pipeline(shapes)
    if not geojson_data:
        logger.error('Erro ao processar shapefiles.')
        sys.exit(1)
    logger.info('Arquivos gerados nos diretórios: files/shapefiles, files/geojson e files/csv')

except Exception as e:
    logger.error(f'Erro: {e}')
