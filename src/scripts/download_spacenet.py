import os
os.chdir("/media/zaxcie/Stock/workspace/home_assessment")

from src.data.map import download_spacenet_dataset



if __name__ == '__main__':
    download_spacenet_dataset("data/spacenet/")
