import numpy as np
from cv2 import (
    GaussianBlur,
    threshold,
    findContours,
    minAreaRect,
    THRESH_BINARY,
    THRESH_OTSU,
    RETR_EXTERNAL,
    CHAIN_APPROX_SIMPLE,
)

class Reel(object):
    def __init__(self, length, image):
        rows, columns = image.shape[:2]
        self.film = np.zeros((length, rows, columns), image.dtype)
        self._index = 0
        self.film[self._index] = image

    def append(self, image):
        self._index = (self._index + 1)%self.film.shape[0]
        self.film[self._index] = image

    @property# this decorator turns the method into a "getter" for the return value so that no "()" are necessary to access it
    def temporalVariance(self):
        avg = self.film.mean(axis = 0)
        return np.absolute(self.film[self._index] - avg)

def motionCenter(image):
    image = GaussianBlur(image.astype("uint8"), (5,5), sigmaX = 0)
    cutoff, image = threshold(image, 0, 255, THRESH_BINARY+THRESH_OTSU)
    if cutoff > 2:
        contours = findContours(image, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)[1]
        centers = []
        for contour in contours:
            centers.append(minAreaRect(contour)[0])
        return np.asarray(centers).mean(axis = 0)
    else:
        return None
