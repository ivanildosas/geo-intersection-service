import os
import pyproj
from pyproj import Geod
import shapely
from shapely import wkt
import fastapi
import uvicorn
from osgeo import ogr, gdal


def check_geojson_file(path):
    print('Verificando arquivo GeoJSON:')
    if os.path.exists(path):
        print(f'    Arquivo encontrado: {path}')
    else:
        print(f'    Arquivo não encontrado: {path}')


# Verifica se as bibliotecas foram importadas
def check_libs():

    print('\nVerificando Bibliotecas:')
    print(f'    Gdal: --------- {gdal.__version__}')
    print(f'    Pyproj: ------- {pyproj.__version__}')
    print(f'    Shapely: ------ {shapely.__version__}')
    print(f'    FastAPI: ------ {fastapi.__version__}')
    print(f'    Uvicorn: ------ {uvicorn.__version__}')
    print(' Bibliotecas importadas com sucesso!\n')


def check(path):
    try:
        check_geojson_file(path)
        check_libs()
    except ImportError as e:
        print(f'Erro de import: {e}')
    except Exception as e:
        print(f'Erro: {e}')
