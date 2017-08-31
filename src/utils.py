import cv2
import numpy as np
from PIL import Image, ImageTk

class Utils(object):

    def draw(self):
        self.__frame__ = cv2.cvtColor(self.__frame__, cv2.COLOR_BGR2RGB)
        pass