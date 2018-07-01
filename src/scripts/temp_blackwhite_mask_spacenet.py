import skimage.io as io
import os


if __name__ == '__main__':
    folder_path = "data/spacenet/rasters/labels/"
    write_folder = "data/spacenet/rasters/mask/"
    for img_name in os.listdir(folder_path):
        img = io.imread(folder_path + img_name)
        img = (img > 0).astype(int)*255

        io.imsave(write_folder + img_name, img)
