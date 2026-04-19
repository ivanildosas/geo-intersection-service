from os import path
from pathlib import Path

# Diretório da aplicação
APP_PATH = path.dirname(path.abspath(__file__))
BASE_DIR = Path(APP_PATH).parent

# Sistema de Referência Geodésico SIRGAS 2000
DATUM = 4674

# Elipsoide
WGS84 = 'WGS84'  # Padrão WebGIS (Leaflet)
GRS80 = 'GRS80'  # Base do SIRGAS 2000
SPHERE = 'sphere'  # OpenStreetMap, ArcGIS Online, Google Maps
ELIPSOID = WGS84

# Diretórios de arquivos
SHAPES_FOLDER = str(BASE_DIR / 'files' / 'shapefiles')
GEOJSON_FOLDER = str(BASE_DIR / 'files' / 'geojson')
CSV_FOLDER = str(BASE_DIR / 'files' / 'csv')

# Shapefiles
SHAPEFILE_NAME_LIST = ['camada-1.shp', 'camada-2.shp', 'camada-3.shp']
SHAPEFILE_PATH_LIST = [str(Path(SHAPES_FOLDER) / x) for x in SHAPEFILE_NAME_LIST]
SHAPEFILE_COUNT = len(SHAPEFILE_NAME_LIST)

# Arquivo GeoJSON
SAMPLE_GEOJSON = 'sample.json'
SAMPLE_GEOJSON_PATH = path.join(GEOJSON_FOLDER, SAMPLE_GEOJSON)

# OUTPUT
OUT_INTERSECT_SHP = path.join(SHAPES_FOLDER, 'output_intersect.shp')
OUT_MEDIA_SHP = path.join(SHAPES_FOLDER, 'output_media_bandas.shp')
OUT_MEDIA_CSV = path.join(CSV_FOLDER, 'attributes_media_bandas.csv')
OUT_MEDIA_JSON = path.join(GEOJSON_FOLDER, 'output_media_bandas.json')
