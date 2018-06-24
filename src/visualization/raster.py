import cv2
import numpy as np

import matplotlib.pyplot as plt


def draw_polygone(img, plygone_coord):
    points = np.array(plygone_coord, np.int32)
    points = points.reshape((-1, 1, 2))
    show_img = cv2.polylines(img, [points], True, (0, 255, 0))

    return show_img