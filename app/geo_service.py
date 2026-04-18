from os import path
from shapely import wkt as shapely_wkt
from pyproj import Geod
from osgeo import osr, ogr, gdal

import app.constants as ct
import app.util as util
from app.field_enum import FieldNames


class GeoService:

    def __init__(self):
        gdal.UseExceptions()
        pass

    # Retorna o valor do atributo do layer
    @staticmethod
    def get_layer_property(layer, field_name):
        if not layer:
            return None
        layer.ResetReading()
        for feature in layer:
            if feature.GetFieldIndex(field_name) != -1:
                val = feature.GetField(field_name)
                if val is not None: # Só aceita se houver dado
                    return val

    # Retorna uma lista de dicionários com os atributos e seus valores do layer
    def get_layer_properties(self, layer):
        if not layer:
            return []

        property_list = []
        layer_defn = layer.GetLayerDefn()
        field_count = layer_defn.GetFieldCount()

        layer.ResetReading()
        for feature in layer:
            prop_dict = {}
            for i in range(field_count):
                field_name = layer_defn.GetFieldDefn(i).GetName()
                value = feature.GetField(i)
                prop_dict[util.fix_charset(field_name)] = value

            property_list.append(prop_dict)
        return property_list

    # Efetua a cálculo geodésico de área em metros quadrados
    @staticmethod
    def get_geodesic_area_m2(ogr_geom, ellipsoid=ct.ELIPSOID):
        if ogr_geom is None:
            return 0.0

        wkt_text = ogr_geom.ExportToWkt()
        shapely_geom = shapely_wkt.loads(wkt_text)

        geod = Geod(ellps=ellipsoid)
        area_m2, _ = geod.geometry_area_perimeter(shapely_geom)
        return abs(area_m2)

    # Verifica se o shapefile tem geometria e atributos
    @staticmethod
    def check_shapefile(file_path):
        try:
            driver = ogr.GetDriverByName("ESRI Shapefile")
            dataset = driver.Open(file_path, 0)

            if dataset is None:
                print(f"Não foi possível abrir {file_path}. Arquivo ausente ou corrompido.")
                return False

            layer = dataset.GetLayer()
            field_count = layer.GetLayerDefn().GetFieldCount()

            if field_count == 0:
                print(f'Não foi possível ler os atributos do shapefile: {path.basename(file_path)}')
                print('Arquivo ausente ou corrompido.')
                return False
            return True
        except Exception as e:
            print(f"ERRO ao validar {file_path}: {e}")
            return False

    # Inclui o atributo 'media' no dataset e preenche seu valor
    @staticmethod
    def create_field_media(dataset, layer_name='Intersect'):
        layer = dataset.GetLayer()
        field_media = ogr.FieldDefn(FieldNames.MEDIA, ogr.OFTReal)
        field_media.SetPrecision(2)
        layer.CreateField(field_media)

        layer_defn = layer.GetLayerDefn()
        layer.ResetReading()
        for feature in layer:
            media = 0.0
            field_count = layer_defn.GetFieldCount()
            for i in range(field_count):
                field_name = layer_defn.GetFieldDefn(i).GetName()
                if field_name.startswith(FieldNames.PREFIX_BANDA):
                    value = feature.GetField(field_name)
                    media += value

            media_value = round((media/ct.SHAPEFILE_COUNT), 2)
            media_index = feature.GetFieldIndex(FieldNames.MEDIA)
            feature.SetField(media_index, media_value)
            layer.SetFeature(feature)
        return dataset

    # Atribui valor aos atributos do dataset e insere os campos 'banda(N)'
    def update_dataset_fields(self, out_dataset, field_dict):
        layer = out_dataset.GetLayer()
        layer_defn = layer.GetLayerDefn()
        field_count = layer_defn.GetFieldCount()

        layer.ResetReading()
        for feature in layer:
            geom = feature.GetGeometryRef()

            # efetua o cálculo de área usando a elipsoid padrão 'WGS84'
            area_m2 = self.get_geodesic_area_m2(geom)
            area_m2 = round(area_m2, 3)

            area_ha = area_m2 / 10000
            area_ha = round(area_ha, 3)

            for i in range(field_count):
                field_name = layer_defn.GetFieldDefn(i).GetName()
                match field_name:
                    case FieldNames.ID_GBA:
                        feature.SetField(i, 1)
                    case FieldNames.AREA_M2:
                        feature.SetField(i, area_m2)
                    case FieldNames.AREA_HA:
                        feature.SetField(i, area_ha)

            # Cria os atributos banda(1..n)
            for i, (key, value) in enumerate(field_dict.items(), start=1):
                field_name = f"{FieldNames.PREFIX_BANDA}{i}"
                field_index = feature.GetFieldIndex(field_name)
                if field_index != -1:
                    val = util.to_float(value) 
                    feature.SetField(field_index, val)

            layer.SetFeature(feature)

    @staticmethod
    def create_spatial_ref(epsg):
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromEPSG(epsg)
        spatial_ref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        return spatial_ref

    # Cria dataset em memória e os atributos ID_GBA, AREA_M2, AREA_HA e banda(1..n)
    def create_memory_dataset(self, new_field_number, new_field_prefix):
        spatial_ref = self.create_spatial_ref(ct.DATUM)
        mem_driver = ogr.GetDriverByName('Memory')
        mem_dset = mem_driver.CreateDataSource("mem_data_source")
        layer = mem_dset.CreateLayer("Intersect", spatial_ref, ogr.wkbMultiPolygon)

        # Cria os Atributos ID_GBA e Área
        layer.CreateField(ogr.FieldDefn(FieldNames.ID_GBA, ogr.OFTInteger))

        field_area_m2 = ogr.FieldDefn(FieldNames.AREA_M2, ogr.OFTReal)
        field_area_m2.SetWidth(24)
        field_area_m2.SetPrecision(3)
        layer.CreateField(field_area_m2)

        field_area_ha = ogr.FieldDefn(FieldNames.AREA_HA, ogr.OFTReal)
        field_area_ha.SetWidth(24)
        field_area_ha.SetPrecision(3)
        layer.CreateField(field_area_ha)

        # Cria os novos atributos
        for i in range(1, new_field_number + 1):
            layer.CreateField(ogr.FieldDefn(f"{new_field_prefix}{i}", ogr.OFTReal))
        return mem_dset

    # Intersecta as geomterias dos 2 datasets
    def intersect_geometries(self, dataset_a, dataset_b):
        layer_a = dataset_a.GetLayer()
        layer_b = dataset_b.GetLayer()

        mem_dset = self.create_memory_dataset(ct.SHAPEFILE_COUNT, FieldNames.PREFIX_BANDA)
        out_layer = mem_dset.GetLayer()

        layer_a.ResetReading()
        for feature_a in layer_a:
            geom_a = feature_a.GetGeometryRef()

            for feature_b in layer_b:
                geom_b = feature_b.GetGeometryRef()
                if geom_a.Intersects(geom_b):
                    out_geom = geom_a.Intersection(geom_b)
                    if out_geom.IsEmpty():
                        continue
                    new_feature = ogr.Feature(out_layer.GetLayerDefn())
                    new_feature.SetGeometry(out_geom)
                    out_layer.CreateFeature(new_feature)
            layer_b.ResetReading()

        return mem_dset

    # Itera a lista de shapes e realiza intersecção booleana
    def intersect_shapes(self, shape_list):
        esri_driver = ogr.GetDriverByName("ESRI Shapefile")
        out_dset = dataset_a = None
        field_dict = {}

        for i in range(1, len(shape_list)):
            if dataset_a is None:
                dataset_a = esri_driver.Open(shape_list[i-1], 0)

            dataset_b = esri_driver.Open(shape_list[i], 0)
            out_dset = self.intersect_geometries(dataset_a, dataset_b)

            # Insere no dicionário o nome e valor do atributo 'value'
            for d_set in [dataset_a, dataset_b]:
                layer = d_set.GetLayer()
                name = layer.GetName()
                if name not in field_dict and d_set.GetDriver().GetName() == 'ESRI Shapefile':
                    value = self.get_layer_property(layer, FieldNames.VALUE)
                    field_dict[name] = value
            # print(f'Dict: {field_dict}', flush=True)
            dataset_a = out_dset
        self.update_dataset_fields(out_dset, field_dict)
        return out_dset

    @staticmethod
    def save_to_shapefile(datasource, file_output_path):
        try:
            driver = ogr.GetDriverByName("ESRI Shapefile")
            if path.exists(file_output_path):
                driver.DeleteDataSource(file_output_path)

            out_dset = driver.CopyDataSource(datasource, file_output_path)

            if out_dset is not None:
                out_dset.FlushCache()
                out_dset = None
                return True

            return False
        except Exception as e:
            print(f"Erro: {e}")
            return False
        finally:
            if out_dset is not None:
                out_dset.FlushCache()
                out_dset = None
