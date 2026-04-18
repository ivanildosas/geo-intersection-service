from shapely import wkt as shapely_wkt
from pyproj import Geod
from osgeo import osr, ogr, gdal

import app.constants as ct
from app.field_enum import FieldNames


class GeoService:

    def __init__(self):
        gdal.UseExceptions()
        pass

    # Cria uma lista de dicionários com os atributos e seus valores
    @staticmethod
    def get_layer_properties(layer):
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
                prop_dict[field_name] = value

            property_list.append(prop_dict)
        return property_list

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

        for i in range(1, len(shape_list)):
            if dataset_a is None:
                dataset_a = esri_driver.Open(shape_list[i-1], 0)

            dataset_b = esri_driver.Open(shape_list[i], 0)
            out_dset = self.intersect_geometries(dataset_a, dataset_b)
            dataset_a = out_dset

        return out_dset
