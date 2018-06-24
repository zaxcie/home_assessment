import numpy as np
import cv2
import os
import json

import matplotlib.pyplot as plt

from src.geo_tools import convert_wgs84geojson_to_pixgeojson
from src.visualization.raster import draw_polygone


PATH_TO_RASTER = "data/spacenet/rasters/"

# TODO script to create proper SpaceNet data. Up to now it was mostly manual copy paste...


class RasterSpaceNet:

    def __init__(self, raster_name, default_data_dir=None):
        if default_data_dir is None:
            self.data_dir = "data/spacenet/rasters/"
        else:
            self.data_dir = default_data_dir

        path_img = self.data_dir + "jpg/RGB-PanSharpen" + raster_name + ".jpg"
        path_geojson = self.data_dir + "geojson/buildings" + raster_name + ".geojson"
        path_tiff = self.data_dir + "tiff/RGB-PanSharpen" + raster_name + ".tif"

        self.path_img = path_img
        self.path_geojson = path_geojson
        self.path_tiff = path_tiff

        self.pixgeo = convert_wgs84geojson_to_pixgeojson(path_geojson,
                                                         path_tiff)

        self.img = self._load_img_from_file(path_img)
        self.geo = self._load_geojson_from_file(path_geojson)
        self.gps_buildings_coords = self._generate_gps_buildings_coords()
        self.pix_buildings_coords = RasterSpaceNet.parse_OGRGeometryShadow_to_string(self.pixgeo)

    @staticmethod
    def parse_OGRGeometryShadow_to_string(geometry):
        str_geometries = list()
        for geo in geometry:
            str_geometry = str(geo["polyPix"])
            str_geometry = str_geometry.replace("POLYGON ", "")
            str_geometry = str_geometry.replace("((", "[[")
            str_geometry = str_geometry.replace("))", "]]")
            str_geometry = str_geometry.replace(",", "],[")
            str_geometry = str_geometry.replace(" ", ",")
            str_geometry = str_geometry.replace(",0", "")
            str_geometries.append(eval(str_geometry))

        return str_geometries

    def _load_img_from_file(self, path):
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return img

    def _generate_gps_buildings_coords(self):
        '''Generate GPS coords
        '''
        buildings = list()
        for feature in self.geo["features"]:
            coords = list()

            for coord in feature["geometry"]["coordinates"][0]:
                coords.append((coord[0], coord[1]))

            buildings.append(coords)

        return buildings

    def _load_geojson_from_file(self, path):
        with open(path, "r") as f:
            geo = json.load(f)

        return geo

    def show(self, overlay=False):
        if overlay:
            plt.imshow(self.img)
            plt.show()
        else:
            show_img = self.img
            for building_coord in self.pix_buildings_coords:
                show_img = draw_polygone(show_img, building_coord)

            plt.imshow(self.img)
            plt.show()


def find_raster_names(path_rasters):
    '''
    Return names of every rasters

    :param path_rasters:
    :return: list, every file names
    '''
    path_taster_jpg = path_rasters + "jpg/"
    names = list()

    for file in os.listdir(path_taster_jpg):
        names.append(file.split(".jpeg"))

    return names


if __name__ == '__main__':
    raster = RasterSpaceNet("__-115.2355626_36.1265426997")

    raster.show()
    pass
