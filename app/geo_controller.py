import os
from app.geo_service import GeoService
import app.constants as ct
from pprint import pprint


class GeoController:
    def __init__(self):
        self.geo_service = GeoService()

    def intersect_pipeline(self):

        print('\nProcessamento iniciado', flush=True)
        for shape_path in ct.SHAPEFILE_PATH_LIST:
            if not self.geo_service.check_shapefile(shape_path):
                raise ValueError(f'Processamento interrompido: {shape_path} inválido.')
        print('(1/6) Validação de arquivos shapefiles concluída.', flush=True)

        # 1. Intersecciona os shapefiles e cria os atributos banda(N)
        result_dataset = self.geo_service.intersect_shapes(ct.SHAPEFILE_PATH_LIST)
        print('(2/6) Intersecção de geometrias concluída.', flush=True)

        # 2. Persiste o resultado da intersecção em arquivo Shapefile
        self.geo_service.save_to_shapefile(result_dataset, ct.OUT_INTERSECT_SHP)
        print(f'(3/6) Shapefile criado com sucesso: {ct.OUT_INTERSECT_SHP}', flush=True)

        geom_layer = result_dataset.GetLayer()
        properties = self.geo_service.get_layer_properties(geom_layer)
        print(properties)

        return properties
