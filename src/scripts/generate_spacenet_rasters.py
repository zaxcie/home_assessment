import os
import skimage.io as io


# For AOL type
AOL_FOLDER_NAMES = ["AOI_2_Vegas_Train", "AOI_3_Paris_Train", "AOI_4_Shanghai_Train", "AOI_5_Khartoum_Train"]
DATA_FOLDER_PATH = "data/spacenet/"
FOLLOWUP_ANNOTATIONS_PATH = "/annotations/annotations/"

IMG_SUFFIX = ".jpg"
MASK_SUFFIX = "segcls.png"

IMG_SIZE = 640

TARGET_FOLDER = "data/spacenet/rasters/"

if __name__ == '__main__':
    for spacenet_city in AOL_FOLDER_NAMES:
        folder_path = DATA_FOLDER_PATH + spacenet_city + FOLLOWUP_ANNOTATIONS_PATH

        for file in os.listdir(folder_path):
            file_path = folder_path + file

            try:
                if file.endswith(".jpg"):
                    target_file_path = TARGET_FOLDER + "/jpg/" + file
                    os.rename(file_path, target_file_path)
                elif file.endswith("segcls.png"):
                    img = io.imread(file_path)
                    img = (img > 0).astype(int) * 255

                    target_file_path = TARGET_FOLDER + "/mask/" + file
                    io.imsave(target_file_path, img)

                    target_file_path = TARGET_FOLDER + "/labels/" + file
                    os.rename(file_path, target_file_path)
                elif file.endswith(".geojson"):
                    # TODO implement
                    target_file_path = TARGET_FOLDER + "/geojson/" + file
                    os.rename(file_path, target_file_path)
            except FileNotFoundError:
                print(file_path)
# TODO Analysis for Rio
# data/spacenet/AOI_2_Vegas_Train/annotations/annotations/RGB-PanSharpen__-115.1636076_36.1230326997segobj.png
