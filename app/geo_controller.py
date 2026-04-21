from os import path
from pathlib import Path
from app.geo_service import GeoService
from app.csv_service import CsvService
from app.json_service import JsonService
import app.constants as ct


class GeoController:
    def __init__(self, app_logger):
        self.app_logger = app_logger
        self.geo_service = GeoService()

    # Pipeline de execução de processamento dos arquivos shapefiles
    def intersect_pipeline(self, layers=None):

        shapes_path_list = ct.SHAPEFILE_PATH_LIST
        if layers is not None:
            shapes_path_list = [str(Path(ct.SHAPES_FOLDER) / x) for x in layers]

        shapes_count = len(shapes_path_list)
        self.app_logger.start('Rotina de processamento espacial iniciada.')

        # 1. Valida os arquivos shapefiles
        for shape_path in shapes_path_list:
            if not self.geo_service.check_shapefile(shape_path):
                self.app_logger.error('Rotina interrompida: shapefile inválido', shape_path, '1/8')
                return None
        self.app_logger.info('Validação de shapefiles concluída.', None, '1/8')

        # 2. Intersecciona os shapefiles e cria os atributos banda(N)
        result_dataset = self.geo_service.intersect_shapes(shapes_path_list)
        if result_dataset is None:
            self.app_logger.error('Rotina interrompida: erro ao interseccionar geometrias.', None, '2/8')
            return None
        self.app_logger.info('Intersecção de geometrias finalizada.', None, '2/8')

        # if result_dataset.GetLayer().GetFeatureCount() == 0:
        # self.app_logger.success('Rotina interrompida: as geometrias de entrada não se intersectam .', None, '2/8')
        # empty_geojson = self.geo_service.datasource_to_geojson(result_dataset)
        # return empty_geojson

        # 3. Persiste a geometria resultante da intersecção em arquivo shapefile
        file_created = self.geo_service.save_to_shapefile(result_dataset, ct.OUT_INTERSECT_SHP)
        if not file_created:
            self.app_logger.error('Rotina interrompida: erro ao gerar shapefile', ct.OUT_INTERSECT_SHP, '3/8')
            return None
        self.app_logger.info('Shapefile gerado:', ct.OUT_INTERSECT_SHP, '3/8')

        # 4 Cria atributo média de bandas
        result_dataset = self.geo_service.create_field_media(result_dataset, shapes_count)
        if result_dataset is None:
            self.app_logger.error('Rotina interrompida: erro ao gerar atributo média de bandas.', None, '4/8')
            return None
        self.app_logger.info('Atributo média de bandas gerado.', None, '4/8')

        # GeoService.get_layer_property(result_dataset.GetLayer())

        # 5. Persiste a geometria com novo atributo em shapefile
        file_created = self.geo_service.save_to_shapefile(result_dataset, ct.OUT_MEDIA_SHP)
        if not file_created:
            self.app_logger.error('Rotina interrompida: erro ao gerar shapefile', ct.OUT_MEDIA_SHP, '5/8')
            return None
        self.app_logger.info('Shapefile gerado:', ct.OUT_MEDIA_SHP, '5/8')

        # 6. Cria CSV com os atributos da geometria resultante da interseção
        props = self.geo_service.get_layer_properties(result_dataset.GetLayer())
        file_created = CsvService.save_attributes_to_csv(props, ct.OUT_MEDIA_CSV)
        if file_created is None:
            self.app_logger.error('Rotina interrompida: erro ao gerar CSV', ct.OUT_MEDIA_CSV, '6/8')
            return None
        elif file_created is False:
            self.app_logger.info('Tabela de atributos vazia, CSV não gerado.', None, '6/8')
        else:
            self.app_logger.info('CSV gerado:', ct.OUT_MEDIA_CSV, '6/8')

        # 7. Cria GeoJSON
        file_created = self.geo_service.save_to_geojson(result_dataset, ct.OUT_MEDIA_JSON)
        if not file_created:
            self.app_logger.error('Rotina interrompida: erro ao gerar GeoJSON', ct.OUT_MEDIA_JSON, '7/8')
            return None
        self.app_logger.info('GeoJSON gerado:', ct.OUT_MEDIA_JSON, '7/8')

        # 8. Ler o arquivo GeoJSON criado
        json_data = JsonService.get_json_data(ct.OUT_MEDIA_JSON)
        if not json_data:

            self.app_logger.error('Rotina interrompida: erro ao ler GeoJSON', ct.OUT_MEDIA_JSON, '8/8')
            return None
        # self.app_logger.info('GeoJSON lido:', ct.OUT_MEDIA_JSON, '8/8')

        self.app_logger.success("Rotina finalizada. Artefatos disponíveis.")

        return json_data

    def get_json_data(self, file_path):
        geojson_data = JsonService.get_json_data(file_path)
        if not geojson_data:
            self.app_logger.error('Erro na leitura do GeoJSON', file_path)
            return None
        self.app_logger.success('GeoJSON lido', file_path)
        return geojson_data

    # Retorna dicionario com as camadas de entrada(shapefiles) em formato GeoJSON Data
    def shapes_to_geojson_dict(self):
        self.app_logger.start('Rotina de conversão de shapefiles para GeoJsonData iniciada.')

        geojson_dict = {}
        shapes_count = len(ct.SHAPEFILE_PATH_LIST_ALL)

        for i, shape_path in enumerate(ct.SHAPEFILE_PATH_LIST_ALL):

            #  nome_camada = f'camada-{i+1}'
            nome_camada = path.basename(shape_path)

            geojson_data = GeoService.shapefile_to_geojson(shape_path)
            if not geojson_data:
                self.app_logger.error('Rotina interrompida: erro na conversão do shapefile', shape_path, f'{i+1}/{shapes_count}')
                return None

            geojson_dict[nome_camada] = geojson_data
            self.app_logger.info('GeoJsonData gerado do shapefile', shape_path, f'{i+1}/{shapes_count}')

        self.app_logger.success('Rotina finalizada.')
        return geojson_dict
