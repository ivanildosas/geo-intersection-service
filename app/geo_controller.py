import os
from app.geo_service import GeoService
from app.csv_service import CsvService
import app.constants as ct
from pprint import pprint


class GeoController:
    def __init__(self):
        self.geo_service = GeoService()

    def intersect_pipeline(self):

        print('\nProcessamento iniciado', flush=True)

        # Valida os arquivos shapefiles
        for shape_path in ct.SHAPEFILE_PATH_LIST:
            if not self.geo_service.check_shapefile(shape_path):
                raise ValueError(f'Processamento interrompido: {shape_path} inválido.')
        print('(1/6) Validação de arquivos shapefiles concluída.', flush=True)

        # 2. Intersecciona os shapefiles e cria os atributos banda(N)
        result_dataset = self.geo_service.intersect_shapes(ct.SHAPEFILE_PATH_LIST)
        print('(2/6) Intersecção de geometrias concluída.', flush=True)

        # 3. Persiste a geometria resultante da intersecção em arquivo Shapefile
        file_created = self.geo_service.save_to_shapefile(result_dataset, ct.OUT_INTERSECT_SHP)
        if not file_created:
            raise ValueError(f'Processamento interrompido: erro ao criar arquivo shapefile: {ct.OUT_INTERSECT_SHP}')
        print(f'(3/6) Arquivo shapefile criado com sucesso: {ct.OUT_INTERSECT_SHP}', flush=True)

        # 4. Cria atributo média na geometria resultante da interseção e persiste em Shapefile
        result_dataset = self.geo_service.create_field_media(result_dataset)
        file_created = self.geo_service.save_to_shapefile(result_dataset, ct.OUT_MEDIA_SHP)
        if not file_created:
            raise ValueError(f'Processamento interrompido: erro ao criar arquivo shapefile: {ct.OUT_MEDIA_SHP}')
        print(f'(4/6) Arquivo shapefile criado com sucesso: {ct.OUT_MEDIA_SHP}')

        # 5. Cria CSV com os atributos da geometria resultante da interseção
        props = self.geo_service.get_layer_properties(result_dataset.GetLayer())
        file_created = CsvService.save_attributes_to_csv(props, ct.OUT_MEDIA_CSV)
        if not file_created:
            raise ValueError(f'Processamento interrompido: erro ao criar arquivo CSV: {ct.OUT_MEDIA_SHP}')
        print(f'(5/6) Arquivo CSV criado com sucesso: {ct.OUT_MEDIA_CSV}')

        geom_layer = result_dataset.GetLayer()
        properties = self.geo_service.get_layer_properties(geom_layer)
        # print(properties)

        return properties
