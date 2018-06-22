from src.utils import append_variable_to_url, download_img_from_url
from src.data.config import GOOGLE_MAP_API_KEY, GOOGLE_MAP_API_STATICMAP_URL

import os


def download_google_satellite_img(addr, url_vars=None, save_dir="data/sat_img/"):
    '''
    :param addr:
    :param url_vars:
    :return:
    '''
    if url_vars is None:
        url_vars = {"zoom": "20",
                    "size": "512x512",
                    "maptype": "satellite",
                    "key": GOOGLE_MAP_API_KEY}

    url_vars.update({"center": addr})

    img_url = append_variable_to_url(GOOGLE_MAP_API_STATICMAP_URL, url_vars)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    download_img_from_url(img_url, save_dir + addr + ".jpg")


def download_spacenet_dataset(path):
    import boto3
    import botocore

    FILES = {
        "processedBuildingLabels.tar.gz": "AOI_1_Rio/processedData/processedBuildingLabels.tar.gz",
        "Rio_BuildingLabels.tar.gz": "AOI_1_Rio/srcData/vectorData/Rio_BuildingLabels.tar.gz",
        "Rio_HGIS_Metro_extract.tar": "AOI_1_Rio/srcData/vectorData/Rio_HGIS_Metro_extract.tar",
        "AOI_2_Vegas_Train.tar.gz": "AOI_2_Vegas/AOI_2_Vegas_Train.tar.gz",
        "AOI_3_Paris_Train.tar.gz": "AOI_3_Paris/AOI_3_Paris_Train.tar.gz",
        "AOI_4_Shanghai_Train.tar.gz": "AOI_4_Shanghai/AOI_4_Shanghai_Train.tar.gz",
        "AOI_5_Khartoum_Train.tar.gz": "AOI_5_Khartoum/AOI_5_Khartoum_Train.tar.gz"
    }

    BUCKET_NAME = 'spacenet-dataset'  # replace with your bucket name

    s3 = boto3.resource('s3')

    for file in FILES:
        try:
            s3.Bucket(BUCKET_NAME).download_file(FILES[file], path + file)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                print("Error" + file)
        print(file)

