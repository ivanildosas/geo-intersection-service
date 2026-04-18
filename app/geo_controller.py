import os
from app.geo_service import GeoService
import app.constants as ct
from pprint import pprint


class GeoController:
    def __init__(self):
        self.geo_service = GeoService()

    def intersect_pipeline(self):

        print('\nProcessamento iniciado')

        # 1. Intersecciona os shapefiles e cria os atributos banda(N)
        result_dataset = self.geo_service.intersect_shapes(ct.SHAPEFILE_PATH_LIST)

        geom_layer = result_dataset.GetLayer()
        properties = self.geo_service.get_layer_properties(geom_layer)

        print(properties)
        print('(1/5) Intersecção de shapes concluída.')

        return properties
