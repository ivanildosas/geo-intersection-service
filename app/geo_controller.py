from app.geo_service import GeoService
from app.csv_service import CsvService
from app.json_service import JsonService
import app.constants as ct
from app.logger import Logger


class GeoController:
    def __init__(self):
        self.geo_service = GeoService()

    # Pipeline de execução de processamento dos arquivos shapefiles
    def intersect_pipeline(self):

        Logger.start('Rotina de processamento espacial iniciada.')

        # 1. Valida os arquivos shapefiles
        for shape_path in ct.SHAPEFILE_PATH_LIST:
            if not self.geo_service.check_shapefile(shape_path):
                Logger.error('Rotina interrompida: shapefile inválido', shape_path, '1/8')
                return None
        Logger.info('Validação de shapefiles concluída.', None, '1/8')

        # 2. Intersecciona os shapefiles e cria os atributos banda(N)
        result_dataset = self.geo_service.intersect_shapes(ct.SHAPEFILE_PATH_LIST)
        if result_dataset is None:
            Logger.error('Rotina interrompida: erro ao interseccionar geometrias.', None, '2/8')
            return None
        Logger.info('Intersecção de geometrias finalizada.', None, '2/8')

        # 3. Persiste a geometria resultante da intersecção em arquivo shapefile
        file_created = self.geo_service.save_to_shapefile(result_dataset, ct.OUT_INTERSECT_SHP)
        if not file_created:
            Logger.error('Rotina interrompida: erro ao gerar shapefile', ct.OUT_INTERSECT_SHP, '3/8')
            return None
        Logger.info('Shapefile gerado:', ct.OUT_INTERSECT_SHP, '3/8')

        # 4 Cria atributo média de bandas
        result_dataset = self.geo_service.create_field_media(result_dataset)
        if result_dataset is None:
            Logger.error('Rotina interrompida: erro ao gerar atributo média de bandas.', None, '4/8')
            return None
        Logger.info('Atributo média de bandas gerado.', None, '4/8')

        # 5. Persiste a geometria com novo atributo em shapefile
        file_created = self.geo_service.save_to_shapefile(result_dataset, ct.OUT_MEDIA_SHP)
        if not file_created:
            Logger.error('Rotina interrompida: erro ao gerar shapefile', ct.OUT_MEDIA_SHP, '5/8')
            return None
        Logger.info('Shapefile gerado:', ct.OUT_MEDIA_SHP, '5/8')

        # 6. Cria CSV com os atributos da geometria resultante da interseção
        props = self.geo_service.get_layer_properties(result_dataset.GetLayer())
        file_created = CsvService.save_attributes_to_csv(props, ct.OUT_MEDIA_CSV)
        if not file_created:
            Logger.error('Rotina interrompida: erro ao gerar CSV', ct.OUT_MEDIA_CSV, '6/8')
            return None
        Logger.info('CSV gerado:', ct.OUT_MEDIA_CSV, '6/8')

        # 7. Cria GeoJSON
        file_created = self.geo_service.save_to_geojson(result_dataset, ct.OUT_MEDIA_JSON)
        if not file_created:
            Logger.error('Rotina interrompida: erro ao gerar GeoJSON', ct.OUT_MEDIA_JSON, '7/8')
            return None
        Logger.info('GeoJSON gerado:', ct.OUT_MEDIA_JSON, '7/8')

        # 8. Ler o arquivo GeoJSON criado
        json_data = JsonService.get_json_data(ct.OUT_MEDIA_JSON)
        if not json_data:
            Logger.error('Rotina interrompida: erro ao ler GeoJSON', ct.OUT_MEDIA_JSON, '8/8')
            return None
        Logger.info('GeoJSON lido:', ct.OUT_MEDIA_JSON, '8/8')
        Logger.success("Rotina finalizada. Artefatos disponíveis.")

        return json_data

    # Retorna dicionario com as camadas de entrada(shapefiles) em formato GeoJSON Data
    def shapes_to_geojson_dict(self):
        Logger.start('Rotina de conversão de shapefiles para GeoJsonData iniciada.')

        count_shapes = len(ct.SHAPEFILE_PATH_LIST)
        geojson_dict = {}

        for i, shape_path in enumerate(ct.SHAPEFILE_PATH_LIST):
            nome_camada = f'camada-{i+1}'
            geojson_data = GeoService.shapefile_to_geojson(shape_path)
            if not geojson_data:
                Logger.error('Rotina interrompida: erro na conversão do shapefile', shape_path, f'{i+1}/{count_shapes}')
                return None

            geojson_dict[nome_camada] = geojson_data
            Logger.info('GeoJsonData gerado do shapefile', shape_path, f'{i+1}/{count_shapes}')

        Logger.success('Rotina finalizada.')
        return geojson_dict
